# import RPi.GPIO as GPIO

# TODO: find the correct pins to use
from src.constants.home_automation import Automation

# third relay
AC_PIN = 11
# first relay
BLOWER_PIN = 15
# second relay
FURNACE_PIN = 13


# GPIO.cleanup()
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(AC_PIN, GPIO.OUT)
# GPIO.setup(FURNACE_PIN, GPIO.OUT)
# GPIO.setup(BLOWER_PIN, GPIO.OUT)


def read_temperature_file():
    return ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES',
            '72 01 4b 46 7f ff 0e 10 57 t=23125']


def turn_on_hvac(device):
     # if device == Automation.HVAC.AIR_CONDITIONING:
     #     GPIO.output(AC_PIN, GPIO.LOW)
     # else:
     #     GPIO.output(FURNACE_PIN, GPIO.LOW)
     # GPIO.output(BLOWER_PIN, GPIO.LOW)
     pass


def turn_off_hvac(device):
    # if device == Automation.HVAC.AIR_CONDITIONING:
    #     GPIO.output(AC_PIN, GPIO.HIGH)
    # else:
    #     GPIO.output(FURNACE_PIN, GPIO.HIGH)
    # GPIO.output(BLOWER_PIN, GPIO.HIGH)
    pass
