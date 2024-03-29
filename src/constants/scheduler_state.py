import uuid

from src.constants.home_automation import Automation
from src.constants.thread_state import AutoHvacState, ManualHvacState
from src.services.thermostat_service import run_auto_thermostat_program, run_manual_thermostat_program
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

    def add_auto_task(self, task):
        task_id = task['task_id']
        if not any(existing_task.THREAD_ID == task_id for existing_task in self.SCHEDULED_TASKS):
            task_state = AutoHvacState(task_id, task['alarm_days'], task['hvac_start'], task['hvac_stop'], task['hvac_start_temp'], task['hvac_stop_temp'])
            task_state.ACTIVE_THREAD = create_thread(lambda: run_auto_thermostat_program(task_state), Automation.TIME.ONE_MINUTE)
            task_state.ACTIVE_THREAD.start()
            self.SCHEDULED_TASKS.append(task_state)

    def remove_task(self, task_id):
        index = next((i for i, x in enumerate(self.SCHEDULED_TASKS) if x.THREAD_ID == task_id), None)
        if index is not None:
            existing_task = self.SCHEDULED_TASKS.pop(index)
            existing_task.ACTIVE_THREAD.stopped.set()

    def add_manual_task(self):
        manual_task = next((task for task in self.SCHEDULED_TASKS if task.IS_MANUAL is True), None)
        if manual_task is not None and not manual_task.ACTIVE_THREAD.is_alive():
            self.remove_task(manual_task.THREAD_ID)
        if not any(existing_task.IS_MANUAL is True for existing_task in self.SCHEDULED_TASKS):
            manual_task = ManualHvacState(str(uuid.uuid4()))
            manual_task.ACTIVE_THREAD = create_thread(run_manual_thermostat_program, Automation.TIME.ONE_MINUTE)
            manual_task.ACTIVE_THREAD.start()
            self.SCHEDULED_TASKS.append(manual_task)

    @staticmethod
    def get_instance():
        if TaskState.__instance is None:
            TaskState.__instance = TaskState()
        return TaskState.__instance
