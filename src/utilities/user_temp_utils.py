import re

from src.utilities.conversion_utils import convert_to_fahrenheit


def get_user_temperature(temp_text, is_fahrenheit):
    if temp_text is None or temp_text[0][-3:] != 'YES':
        return 0.0
    temp_string = re.search('(t=\d*)', temp_text[1])
    if temp_string is None:
        return 0.0

    celsius = _get_celsius_value(temp_string.group())
    return _convert_to_correct_unit(celsius, is_fahrenheit)


def _get_celsius_value(temp_row):
    cleaned_text = temp_row.replace('t=', '')
    temp_celsius = int(cleaned_text)
    return round(temp_celsius / 1000, 2)


def _convert_to_correct_unit(celsius, is_fahrenheit):
    if is_fahrenheit:
        return convert_to_fahrenheit(celsius)
    return celsius
