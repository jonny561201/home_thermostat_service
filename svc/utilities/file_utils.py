import json

from svc.config.settings_state import Settings
from svc.constants.home_automation import Hvac


def get_api_key():
    file_name = Settings.get_instance().api_key_file
    try:
        with open(file_name, 'r+', encoding='utf-8') as file:
            content = json.load(file)
        return content['api_key']
    except FileNotFoundError:
        return None


def save_api_key(api_key):
    file_name = Settings.get_instance().api_key_file
    with open(file_name, 'w+', encoding='utf-8') as file:
        content = {'api_key': api_key}
        json.dump(content, file)


def get_desired_state():
    file_name = Settings.get_instance().state_file
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return __create_file_if_not_exist(file_name)


def save_desired_state(desired_temp, mode):
    file_name = Settings.get_instance().state_file
    with open(file_name, 'w+', encoding='utf-8') as file:
        json.dump({'desiredTemp': desired_temp, 'mode': mode}, file)


def get_schedule():
    file_name = Settings.get_instance().schedule_file
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_schedule(tasks):
    file_name = Settings.get_instance().schedule_file
    with open(file_name, 'w+', encoding='utf-8') as file:
        json.dump(tasks, file)


def __create_file_if_not_exist(file_name):
    content = {'desiredTemp': Hvac.DEFAULT_DESIRED_TEMP, 'mode': Hvac.MODE.TURN_OFF}
    with open(file_name, 'w+', encoding='utf-8') as file:
        json.dump(content, file)
    return content
