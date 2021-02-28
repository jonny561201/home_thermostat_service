import json

from src.constants.home_automation import Automation
from src.constants.settings_state import Settings


def get_desired_temp():
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, TypeError):
        content = {'desiredTemp': 21.1111, 'mode': Automation.HVAC.MODE.TURN_OFF}
        with open(file_name, "w+") as file:
            json.dump(content, file)
        return content
