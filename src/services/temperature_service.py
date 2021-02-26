from src.utilities.gpio_utils import read_temperature_file
from src.utilities.user_temp_utils import get_user_temperature


def get_internal_temp(preference):
    temp_text = read_temperature_file()
    return get_user_temperature(temp_text, preference['is_fahrenheit'])
