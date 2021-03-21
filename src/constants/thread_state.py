from datetime import datetime, time

from src.constants.settings_state import Settings
from src.utilities.api_utils import get_weather_data_by_user
from src.utilities.conversion_utils import convert_to_celsius


class ThreadState:
    ACTIVE_THREAD = None
    THREAD_ID = None


class HvacState(ThreadState):
    TRIGGERED = False
    START_TIME = None
    STOP_TIME = None
    START_TEMP = None
    STOP_TEMP = None
    DAYS = None
    DAILY_TEMP = None

    def __init__(self, task_id: str, days: str, start: str, stop: str, start_temp: int, stop_temp: int):
        self.THREAD_ID = task_id
        self.DAYS = days
        self.START_TEMP = start_temp
        self.STOP_TEMP = stop_temp
        self.START_TIME = time.fromisoformat(start)
        self.STOP_TIME = time.fromisoformat(stop)

    # TODO: have the state object query the daily high temp (cache it and requery each day once when rolls over)
    # TODO: if the api comes throws save as None and requery
    def get_daily_high(self):
        time = datetime.now().time()
        if time.hour == 0 and time.minute == 1 or time.minute == 0:
            self.DAILY_TEMP = None
        if self.DAILY_TEMP is not None:
            return self.DAILY_TEMP
        else:
            user_id = Settings.get_instance().user_id
            response = get_weather_data_by_user(user_id)
            if response['isFahrenheit']:
                celsius = convert_to_celsius(response['maxTemp'])
                self.DAILY_TEMP = celsius
                return celsius
            self.DAILY_TEMP = response['maxTemp']
            return response['maxTemp']
