#                  - OpenPLC Python SubModule (PSM) -
# 
# PSM is the bridge connecting OpenPLC core to Python programs. PSM allows
# you to directly interface OpenPLC IO using Python and even write drivers 
# for expansion boards using just regular Python.
#
# PSM API is quite simple and just has a few functions. When writing your
# own programs, avoid touching on the "__main__" function as this regulates
# how PSM works on the PLC cycle. You can write your own hardware initialization
# code on hardware_init(), and your IO handling code on update_inputs() and
# update_outputs()
#
# To manipulate IOs, just use PSM calls psm.get_var([location name]) to read
# an OpenPLC location and psm.set_var([location name], [value]) to write to
# an OpenPLC location. For example:
#     psm.get_var("QX0.0")
# will read the value of %QX0.0. Also:
#     psm.set_var("IX0.0", True)
# will set %IX0.0 to true.
#
# Below you will find a simple example that uses PSM to switch OpenPLC's
# first digital input (%IX0.0) every second. Also, if the first digital
# output (%QX0.0) is true, PSM will display "QX0.0 is true" on OpenPLC's
# dashboard. Feel free to reuse this skeleton to write whatever you want.

#import all your libraries here
import psm
import time
import RPi.GPIO as GPIO
import adafruit_tcs34725

#GPIO Mode
GPIO.setmode(GPIO.BCM)

GPIO_RANGE_TRIGGER = 23
GPIO_RANGE_ECHO = 24
GPIO_PUMP = 25
GPIO_DOSE_RED = 8
GPIO_DOSE_BLUE = 12

#global variables
counter = 0
var_state = False

def hardware_init():
    global i2c
    global rgbsensor
    #Insert your hardware initialization code in here
    psm.start()
    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    GPIO.setup(GPIO_PUMP, GPIO.OUT)
    GPIO.setup(GPIO_DOSE_RED, GPIO.OUT)
    GPIO.setup(GPIO_DOSE_BLUE, GPIO.OUT)
    i2c = board.I2C()  # uses board.SCL and board.SDA
    rgbsensor = adafruit_tcs34725.TCS34725(i2c)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def update_inputs():
    #place here your code to update inputs
    distance = distance()
    color_rgb = sensor.color_rgb_bytes
    psm.set_var("IW0", color_rgb[0])
    psm.set_var("IW1", color_rgb[1])
    psm.set_var("IW2", color_rgb[2])
    psm.set_var("ID0", distance)
        
    
    
def update_outputs():
    #place here your code to work on outputs
    pump = GPIO.HIGH if psm.get_var("QX0.4") else GPIO.LOW
    doser_red = GPIO.HIGH if psm.get_var("QX0.6") else GPIO.LOW
    doser_blue = GPIO.HIGH if psm.get_var("QX0.7") else GPIO.LOW
    GPIO.output(GPIO_PUMP,pump)
    GPIO.output(GPIO_DOSE_RED, doser_red)
    GPIO.output(GPIO_DOSE_BLUE, doser_blue)

if __name__ == "__main__":
    hardware_init()
    while (not psm.should_quit()):
        update_inputs()
        update_outputs()
        time.sleep(0.1) #You can adjust the psm cycle time here
    psm.stop()


