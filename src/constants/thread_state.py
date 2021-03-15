import datetime


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

    def __init__(self, task_id: str, days: str, start: datetime.time, stop: datetime.time, start_temp: int, stop_temp: int):
        self.THREAD_ID = task_id
        self.DAYS = days
        self.START_TEMP = start_temp
        self.STOP_TEMP = stop_temp
        self.START_TIME =start
        self.STOP_TIME = stop
