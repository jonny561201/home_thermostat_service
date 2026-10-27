from datetime import datetime, time

from svc.config.hvac_state import HvacState
from svc.constants.home_automation import Automation
from svc.utilities import file_utils
from svc.utilities import gpio_utils
from svc.utilities.user_temp_utils import get_user_temperature


def run_thermostat():
    celsius_temp = get_user_temperature(gpio_utils.read_temperature_file(), False)
    if celsius_temp is None:
        stop_hvac()
        return
    state = file_utils.get_desired_state()
    if state['mode'] == Automation.HVAC.MODE.AUTO:
        mode, desired_temp = __resolve_scheduled_target(file_utils.get_schedule(), datetime.now())
    else:
        mode, desired_temp = state['mode'], state['desiredTemp']
    hvac_state = HvacState.get_instance()
    if not __is_allowed(hvac_state.active_device, mode):
        stop_hvac()
        return
    desired_device = __choose_device(celsius_temp, mode, desired_temp, hvac_state.active_device)
    __switch_to(hvac_state, desired_device)


def stop_hvac():
    gpio_utils.turn_off_hvac(Automation.HVAC.AIR_CONDITIONING)
    gpio_utils.turn_off_hvac(Automation.HVAC.FURNACE)
    hvac_state = HvacState.get_instance()
    if hvac_state.active_device != None:
        hvac_state.record_change(None)


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


def __is_allowed(active_device, mode):
    if mode not in (Automation.HVAC.MODE.HEATING, Automation.HVAC.MODE.COOLING, Automation.HVAC.MODE.AUTO):
        return False
    if active_device == Automation.HVAC.FURNACE:
        return mode != Automation.HVAC.MODE.COOLING
    if active_device == Automation.HVAC.AIR_CONDITIONING:
        return mode != Automation.HVAC.MODE.HEATING
    return True


def __choose_device(celsius_temp, mode, desired_temp, active_device):
    if active_device == Automation.HVAC.FURNACE and celsius_temp < desired_temp:
        return Automation.HVAC.FURNACE
    if active_device == Automation.HVAC.AIR_CONDITIONING and celsius_temp > desired_temp:
        return Automation.HVAC.AIR_CONDITIONING
    band = Automation.HVAC.AUTO_BAND if mode == Automation.HVAC.MODE.AUTO else Automation.HVAC.DEADBAND
    if mode != Automation.HVAC.MODE.COOLING and celsius_temp < desired_temp - band:
        return Automation.HVAC.FURNACE
    if mode != Automation.HVAC.MODE.HEATING and celsius_temp > desired_temp + band:
        return Automation.HVAC.AIR_CONDITIONING
    return None


def __switch_to(hvac_state, desired_device):
    if desired_device == hvac_state.active_device:
        return
    if hvac_state.active_device != None:
        if hvac_state.seconds_since_change() < Automation.HVAC.MIN_ON_SECONDS:
            return
        gpio_utils.turn_off_hvac(hvac_state.active_device)
        hvac_state.record_change(None)
        return
    if hvac_state.seconds_since_change() < Automation.HVAC.MIN_OFF_SECONDS:
        return
    gpio_utils.turn_on_hvac(desired_device)
    hvac_state.record_change(desired_device)
