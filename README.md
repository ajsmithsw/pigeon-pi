# pigeon-pi

## Prerequisites
install the following onto raspberry pi:

Note: Some versions of opencv-python are not compatible with raspi, check docs:
    
    $ pip3 install opencv-python==3.4.6.27
    
openCV dependencies:
    
    $ sudo apt-get install libatlas-base-dev
    $ sudo apt-get install libjasper-dev
    $ sudo apt-get install libqtqui4
    $ sudo apt-get install python3-pyqt5
    $ sudo apt install libqt4-test
    
imutils library for useful helper functions (assumes numpy and opencv installed):
    
    $ pip install imutils
    
// TODO: Create bash script to install dependencies

## Informational Resources
- https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/