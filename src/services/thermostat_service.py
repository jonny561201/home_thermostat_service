from src.constants.home_automation import Automation
from src.utilities import gpio_utils
from src.utilities.file_utils import get_desired_temp
from src.utilities.user_temp_utils import get_user_temperature


# TODO: determine mode HEAT/COOL
# TODO: when file mode is not none run normal program
# TODO: when inside schedule event turn on when below desired temp (reverse cool)
# TODO: when inside scheduled event turn off when at or above desired temp (reverse cool)
# TODO: when outside scheduled event turn on when below desired temp (reverse cool)
# TODO: when outside scheduled event turn off when above desired (reverse cool)
def run_thermostat_program(event_state):
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
