from datetime import time

import requests

from src.constants.settings_state import Settings


def get_hvac_tasks_by_user(user_id):
    base_url = Settings.get_instance().hub_base_url
    try:
        response = requests.get(f'{base_url}/userId/{user_id}/tasks/hvac', timeout=5)
        activities_response = response.json()
        for task in activities_response:
            task['alarm_time'] = None if task.get('alarm_time') is None else time.fromisoformat(task['alarm_time'])
        return activities_response
    except Exception:
        return None
