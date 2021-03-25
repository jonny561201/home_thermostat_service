from datetime import datetime, time

from src.constants.settings_state import Settings
from src.utilities.api_utils import get_weather_data_by_user
from src.utilities.conversion_utils import convert_to_celsius


class ThreadState:
    ACTIVE_THREAD = None
    THREAD_ID = None


class AutoHvacState(ThreadState):
    START_TIME = None
    STOP_TIME = None
    START_TEMP = None
    STOP_TEMP = None
    DAYS = None
    DAILY_TEMP = None

    def __init__(self, task_id: str, days: str, start: str, stop: str, start_temp: float, stop_temp: float):
        self.THREAD_ID = task_id
        self.DAYS = days
        self.START_TEMP = start_temp
        self.STOP_TEMP = stop_temp
        self.START_TIME = time.fromisoformat(start)
        self.STOP_TIME = time.fromisoformat(stop)

    def get_daily_high(self):
        current_time = datetime.now().time()
        if current_time.hour == 0 and current_time.minute == 1 or current_time.minute == 0:
            self.DAILY_TEMP = None
        if self.DAILY_TEMP is not None:
            return self.DAILY_TEMP
        else:
            return self.__get_cache_max_temp()

    def __get_cache_max_temp(self):
        user_id = Settings.get_instance().user_id
        response = get_weather_data_by_user(user_id)
        if response is None:
            self.DAILY_TEMP = None
            return None
        temp = response['maxTemp']
        if response['isFahrenheit']:
            temp = convert_to_celsius(response['maxTemp'])
        self.DAILY_TEMP = temp
        return temp
