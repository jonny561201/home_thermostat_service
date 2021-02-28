from src.constants.home_automation import Automation
from src.utilities import gpio_utils
from src.utilities.file_utils import get_desired_temp
from src.utilities.user_temp_utils import get_user_temperature


# TODO: do I need an HVAC state object or do I just always read the file...probably
def run_thermostat_program():
    temp_file = gpio_utils.read_temperature_file()
    celsius_temp = get_user_temperature(temp_file, False)
    state = get_desired_temp()

    if state['mode'] == Automation.HVAC.MODE.COOLING and celsius_temp > state['desiredTemp']:
        gpio_utils.turn_on_hvac(Automation.HVAC.AIR_CONDITIONING)
    elif state['mode'] == Automation.HVAC.MODE.HEATING and celsius_temp < state['desiredTemp']:
        gpio_utils.turn_on_hvac(Automation.HVAC.FURNACE)
    else:
        gpio_utils.turn_off_hvac(Automation.HVAC.AIR_CONDITIONING)
        gpio_utils.turn_off_hvac(Automation.HVAC.FURNACE)

