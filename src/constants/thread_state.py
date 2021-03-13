import datetime


class ThreadState:
    ACTIVE_THREAD = None
    THREAD_ID = None


class HvacState(ThreadState):
    TRIGGERED = False
    START_TIME = None
    STOP_TIME = None
    DAYS = None

    def __init__(self, task_id: str, days: str, start: datetime.time, stop: datetime.time, ):
        self.THREAD_ID = task_id
        self.DAYS = days
        self.START_TIME = datetime.datetime.combine(datetime.date.today(), start).time()
        self.STOP_TIME = datetime.datetime.combine(datetime.date.today(), stop).time()
