from datetime import datetime

from src.constants.home_automation import Automation
from src.utilities import gpio_utils
from src.utilities.file_utils import get_desired_temp
from src.utilities.user_temp_utils import get_user_temperature


def run_thermostat_program(event_state):
    temp_file = gpio_utils.read_temperature_file()
    celsius_temp = get_user_temperature(temp_file, False)
    state = get_desired_temp()

    if state['mode'] is None:
        __run_automated_hvac(celsius_temp, event_state)
    else:
        __run_manual_hvac(celsius_temp, state['mode'], state['desiredTemp'])


def __run_automated_hvac(celsius_temp, event_state):
    mode = __calculate_mode(event_state, celsius_temp)
    if event_state.START_TIME <= datetime.now().time() < event_state.STOP_TIME:
        __run_manual_hvac(celsius_temp, mode, event_state.START_TEMP)
    else:
        __run_manual_hvac(celsius_temp, mode, event_state.STOP_TEMP)


def __run_manual_hvac(celsius_temp, mode, desired_temp):
    if mode == Automation.HVAC.MODE.COOLING and celsius_temp > desired_temp:
        gpio_utils.turn_on_hvac(Automation.HVAC.AIR_CONDITIONING)
    elif mode == Automation.HVAC.MODE.HEATING and celsius_temp < desired_temp:
        gpio_utils.turn_on_hvac(Automation.HVAC.FURNACE)
    else:
        gpio_utils.turn_off_hvac(Automation.HVAC.AIR_CONDITIONING)
        gpio_utils.turn_off_hvac(Automation.HVAC.FURNACE)


def __calculate_mode(event_state, celsius_temp):
    daily_high = event_state.get_daily_high()
    if daily_high is None:
        return Automation.HVAC.MODE.TURN_OFF
    elif daily_high > 22 and celsius_temp > Automation.HVAC.MIN_COOLING:
        return Automation.HVAC.MODE.COOLING
    elif daily_high < 18 and celsius_temp < Automation.HVAC.MAX_HEATING:
        return Automation.HVAC.MODE.HEATING
    elif celsius_temp <= Automation.HVAC.MIN_COOLING:
        return Automation.HVAC.MODE.HEATING
    else:
        return Automation.HVAC.MODE.TURN_OFF
