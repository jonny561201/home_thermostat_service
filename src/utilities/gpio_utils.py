# import RPi.GPIO as GPIO

# TODO: find the correct pins to use
import os
from glob import glob

from src.constants.home_automation import Automation

# third relay
AC_PIN = 11
# first relay
BLOWER_PIN = 15
# second relay
FURNACE_PIN = 13
THERMO_PIN = 11


# GPIO.cleanup()
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(AC_PIN, GPIO.OUT)
# GPIO.setup(FURNACE_PIN, GPIO.OUT)
# GPIO.setup(BLOWER_PIN, GPIO.OUT)
# GPIO.setup(THERMO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def read_temperature_file():
    base_dir = '/sys/bus/w1/devices/'
    file_name = "w1_slave"
    try:
        device_folder = glob(base_dir + '28-*')[0]
        with open(os.path.join(device_folder, file_name), 'r', encoding='utf-8') as file:
            return file.read().split("\n")
    except Exception:
        return None


def turn_on_hvac(device):
    # if device == Automation.HVAC.AIR_CONDITIONING:
    #     GPIO.output(AC_PIN, GPIO.HIGH)
    # else:
    #     GPIO.output(FURNACE_PIN, GPIO.HIGH)
    # GPIO.output(BLOWER_PIN, GPIO.HIGH)
    pass


def turn_off_hvac(device):
    # if device == Automation.HVAC.AIR_CONDITIONING:
    #     GPIO.output(AC_PIN, GPIO.LOW)
    # else:
    #     GPIO.output(FURNACE_PIN, GPIO.LOW)
    # GPIO.output(BLOWER_PIN, GPIO.LOW)
    pass
