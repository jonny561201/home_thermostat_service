import logging

from src.constants.home_automation import Automation
from src.constants.thread_state import HvacState
from src.services.thermostat_service import run_thermostat_program
from src.utilities.event_utils import create_thread


class TaskState:
    __instance = None
    API_KEY = None
    SCHEDULED_TASKS = []

    def __init__(self):
        if TaskState.__instance is not None:
            raise Exception
        else:
            TaskState.__instance = self

    def add_hvac_task(self, task_id, days, start_time, stop_time):
        if not any(task.THREAD_ID == task_id for task in self.SCHEDULED_TASKS):
            logging.info(f'-----added new hvac task id: {task_id}-----')
            task_state = HvacState(task_id, days, start_time, stop_time)
            task_state.ACTIVE_THREAD = create_thread(lambda: run_thermostat_program(task_state), Automation.TIME.ONE_MINUTE)
            task_state.ACTIVE_THREAD.start()
            self.SCHEDULED_TASKS.append(task_state)

    def remove_task(self, task_id):
        index = next((i for i, x in enumerate(self.SCHEDULED_TASKS) if x.THREAD_ID == task_id), None)
        if index is not None:
            logging.info(f'-----removed hvac task id: {task_id}-----')
            existing_task = self.SCHEDULED_TASKS.pop(index)
            existing_task.ACTIVE_THREAD.stopped.set()

    @staticmethod
    def get_instance():
        if TaskState.__instance is None:
            TaskState.__instance = TaskState()
        return TaskState.__instance
