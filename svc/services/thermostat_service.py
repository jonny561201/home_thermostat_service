from datetime import datetime, time

from svc.constants.home_automation import Automation
from svc.utilities import file_utils
from svc.utilities import gpio_utils
from svc.utilities.user_temp_utils import get_user_temperature


def run_thermostat():
    temp_file = gpio_utils.read_temperature_file()
    if temp_file is None:
        return
    celsius_temp = get_user_temperature(temp_file, False)
    state = file_utils.get_desired_state()
    if state['mode'] == Automation.HVAC.MODE.AUTO:
        mode, desired_temp = __resolve_scheduled_target(file_utils.get_schedule(), datetime.now())
    else:
        mode, desired_temp = state['mode'], state['desiredTemp']
    __run_hvac(celsius_temp, mode, desired_temp)


def __resolve_scheduled_target(tasks, now):
    today = now.strftime('%a')
    todays_tasks = [task for task in tasks if today in (task.get('alarmDays') or '')]
    for task in todays_tasks:
        if task.get('hvacStart') is None or task.get('hvacStop') is None:
            continue
        if time.fromisoformat(task['hvacStart']) < now.time() < time.fromisoformat(task['hvacStop']):
            return task['hvacMode'], task['hvacStartTemp']
    if len(todays_tasks) > 0:
        return todays_tasks[0]['hvacMode'], todays_tasks[0]['hvacStopTemp']
    return Automation.HVAC.MODE.TURN_OFF, None


def __run_hvac(celsius_temp, mode, desired_temp):
    if mode == Automation.HVAC.MODE.COOLING and celsius_temp > desired_temp:
        __turn_on(Automation.HVAC.AIR_CONDITIONING, Automation.HVAC.FURNACE)
    elif mode == Automation.HVAC.MODE.HEATING and celsius_temp < desired_temp:
        __turn_on(Automation.HVAC.FURNACE, Automation.HVAC.AIR_CONDITIONING)
    elif mode == Automation.HVAC.MODE.AUTO and celsius_temp < desired_temp - Automation.HVAC.AUTO_BAND:
        __turn_on(Automation.HVAC.FURNACE, Automation.HVAC.AIR_CONDITIONING)
    elif mode == Automation.HVAC.MODE.AUTO and celsius_temp > desired_temp + Automation.HVAC.AUTO_BAND:
        __turn_on(Automation.HVAC.AIR_CONDITIONING, Automation.HVAC.FURNACE)
    else:
        __turn_all_off()


def __turn_on(device, opposite_device):
    gpio_utils.turn_off_hvac(opposite_device)
    gpio_utils.turn_on_hvac(device)


def __turn_all_off():
    gpio_utils.turn_off_hvac(Automation.HVAC.AIR_CONDITIONING)
    gpio_utils.turn_off_hvac(Automation.HVAC.FURNACE)
