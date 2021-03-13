import logging

from src.constants.scheduler_state import TaskState
from src.constants.settings_state import Settings
from src.utilities.api_utils import get_hvac_tasks_by_user


def schedule_hvac_tasks():
    try:
        light_state = TaskState.get_instance()
        light_tasks = get_hvac_tasks_by_user(Settings.get_instance().user_id)
        if light_tasks is not None:
            enabled_tasks = [task for task in light_tasks if task['enabled']]
            __add_new_alarms(light_state, enabled_tasks)
            __remove_cancelled_alarms(light_state, enabled_tasks)
    except Exception as er:
        logging.error(er)


def __add_new_alarms(light_state, light_tasks):
    for task in light_tasks:
        if task['hvac_start'] is not None and task['hvac_stop'] is not None and task['alarm_days'] is not None:
            task_id = task['task_id']
            light_state.add_hvac_task(task_id, task['alarm_days'], task['hvac_start'], task['hvac_stop'])


def __remove_cancelled_alarms(light_state, light_tasks):
    alarm_ids = {alarm.THREAD_ID for alarm in light_state.SCHEDULED_TASKS}
    request_ids = {task['task_id'] for task in light_tasks}
    missing_items = alarm_ids - request_ids
    for item in missing_items:
        light_state.remove_task(item)
