import logging
from threading import Thread, Event

from src.constants.home_automation import Automation


class MyThread(Thread):
    def __init__(self, event, sched_function, function_interval):
        Thread.__init__(self)
        self.stopped = event
        self.function = sched_function
        self.interval = function_interval

    def run(self):
        try:
            while not self.stopped.wait(self.interval):
                try:
                    self.function()
                except Exception as e:
                    logging.error(f'Exception thrown invoking function')
                    logging.error(e)
        except Exception as e:
            logging.error(f'Exception thrown during initial running of thread')
            logging.error(e)


# thread.stopped.set() will kill the process
def create_thread(fn, delay=Automation.TIME.THIRTY_SECONDS):
    stop_event = Event()
    return MyThread(stop_event, fn, delay)
