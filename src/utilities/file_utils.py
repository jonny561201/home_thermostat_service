import json

from src.constants.settings_state import Settings


def get_desired_temp():
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, TypeError):
        return None
