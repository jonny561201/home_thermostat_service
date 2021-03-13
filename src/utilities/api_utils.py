from datetime import time

import requests

from src.constants.settings_state import Settings


def get_hvac_tasks_by_user(user_id):
    base_url = Settings.get_instance().hub_base_url
    try:
        response = requests.get(f'{base_url}/userId/{user_id}/tasks', timeout=5)
        light_response = response.json()
        for task in light_response:
            task['alarm_time'] = None if task.get('alarm_time') is None else time.fromisoformat(task['alarm_time'])
        return light_response
    except Exception:
        return None
