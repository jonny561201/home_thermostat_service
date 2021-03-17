import requests

from src.constants.settings_state import Settings


def get_hvac_tasks_by_user(user_id):
    base_url = Settings.get_instance().hub_base_url
    try:
        response = requests.get(f'{base_url}/userId/{user_id}/tasks/hvac', timeout=5)
        return response.json()
    except Exception:
        return None


def get_weather_data_by_user(user_id):
    base_url = Settings.get_instance().hub_base_url
    requests.get(f'{base_url}/temperature/{user_id}')
