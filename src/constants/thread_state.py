from datetime import time


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
        return self.DAILY_TEMP
