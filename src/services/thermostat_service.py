from src.constants.home_automation import Automation
from src.constants.hvac_state import HvacState
from src.utilities import gpio_utils
from src.utilities.gpio_utils import read_temperature_file
from src.utilities.user_temp_utils import get_user_temperature


def run_thermostat_program():
    temp_file = read_temperature_file()
    celsius_temp = get_user_temperature(temp_file, False)
    state = HvacState.get_instance()

    if state.MODE == Automation.HVAC.MODE.COOLING and celsius_temp > state.DESIRED_TEMP:
        gpio_utils.turn_on_hvac(Automation.HVAC.AIR_CONDITIONING)
    elif state.MODE == Automation.HVAC.MODE.HEATING and celsius_temp < state.DESIRED_TEMP:
        gpio_utils.turn_on_hvac(Automation.HVAC.FURNACE)
    else:
        gpio_utils.turn_off_hvac(Automation.HVAC.AIR_CONDITIONING)
        gpio_utils.turn_off_hvac(Automation.HVAC.FURNACE)

