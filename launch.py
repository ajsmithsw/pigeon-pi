from picamera.array import PiRGBArray
from picamera import PiCamera
from gpiozero import LED
import argparse
import warnings
import datetime
import cv2
import imutils
import json
import time

# Argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")
args = vars(ap.parse_args())

# filter warnings and load config
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

# Setup LED indicators (optional)
blue = LED(17)
white = LED(27)

# Setup camera
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
stream = PiRGBArray(camera, size=tuple(conf["resolution"]))

# Allow camera to warm up, initialize average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
blue.on()
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

# capture the frames from the camera
for f in camera.capture_continuous(stream, format="bgr", use_video_port=True):
    frame = f.array
    timestamp = datetime.datetime.now()
    motion_detected = False

    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        stream.truncate(0)
        continue

    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    threshold = cv2.threshold(frameDelta, conf["delta_threshold"], 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None, iterations=2)
    contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    for c in contours:
        if cv2.contourArea(c) < conf["min_area"]:
            motion_detected = False
            white.off()
            continue

        # compute bounding box
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        motion_detected = True

    white.on()

    ts = timestamp.strftime("%A %d %B %Y %I:%M:%Sp")
    cv2.putText(frame, "Motion Detected", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # Show video feed
    if conf["show_video"]:
        cv2.imshow("Feed", frame)

        # Quit using the 'q' key
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    stream.truncate(0)
