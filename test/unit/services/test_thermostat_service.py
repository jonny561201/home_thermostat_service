from datetime import datetime

from mock import patch, call, MagicMock

from svc.constants.home_automation import Automation
from svc.services.thermostat_service import run_thermostat, stop_hvac


@patch('svc.services.thermostat_service.HvacState')
@patch('svc.services.thermostat_service.datetime')
@patch('svc.services.thermostat_service.file_utils')
@patch('svc.services.thermostat_service.gpio_utils')
@patch('svc.services.thermostat_service.get_user_temperature')
class TestRunThermostat:
    TEMP_TEXT = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES', '72 01 4b 46 7f ff 0e 10 57 t=21000']
    MONDAY_NOON = datetime(2026, 10, 26, 12, 0, 0)
    MONDAY_NIGHT = datetime(2026, 10, 26, 23, 0, 0)
    LONG_AGO = 600
    RECENTLY = 60

    def setup_method(self):
        self.HVAC = MagicMock(active_device=None)
        self.HVAC.seconds_since_change.return_value = self.LONG_AGO
        self.TASK = {'taskId': 'task-1', 'alarmDays': 'MonWed', 'hvacStart': '06:00:00', 'hvacStop': '22:00:00',
                     'hvacStartTemp': 22.0, 'hvacStopTemp': 18.0, 'hvacMode': Automation.HVAC.MODE.HEATING}

    def __arrange(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, current_temp, mode, desired_temp=21.0, tasks=None, now=None):
        mock_gpio.read_temperature_file.return_value = self.TEMP_TEXT
        mock_temp.return_value = current_temp
        mock_file.get_desired_state.return_value = {'desiredTemp': desired_temp, 'mode': mode}
        mock_file.get_schedule.return_value = tasks if tasks is not None else []
        mock_datetime.now.return_value = now if now is not None else self.MONDAY_NOON
        mock_hvac.get_instance.return_value = self.HVAC

    def test_run_thermostat__should_read_temperature_in_celsius(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 21.0, Automation.HVAC.MODE.HEATING)

        run_thermostat()

        mock_temp.assert_called_once_with(self.TEMP_TEXT, False)

    def test_run_thermostat__should_turn_everything_off_immediately_when_sensor_fails(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, None, Automation.HVAC.MODE.HEATING)
        self.HVAC.active_device = Automation.HVAC.FURNACE
        self.HVAC.seconds_since_change.return_value = self.RECENTLY

        run_thermostat()

        mock_gpio.turn_off_hvac.assert_has_calls([call(Automation.HVAC.AIR_CONDITIONING), call(Automation.HVAC.FURNACE)])
        self.HVAC.record_change.assert_called_once_with(None)
        mock_file.get_desired_state.assert_not_called()

    def test_run_thermostat__should_turn_everything_off_immediately_when_mode_off(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 15.0, Automation.HVAC.MODE.TURN_OFF)
        self.HVAC.active_device = Automation.HVAC.FURNACE
        self.HVAC.seconds_since_change.return_value = self.RECENTLY

        run_thermostat()

        mock_gpio.turn_off_hvac.assert_has_calls([call(Automation.HVAC.AIR_CONDITIONING), call(Automation.HVAC.FURNACE)])
        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_turn_off_furnace_immediately_when_mode_switches_to_cooling(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 18.0, Automation.HVAC.MODE.COOLING)
        self.HVAC.active_device = Automation.HVAC.FURNACE
        self.HVAC.seconds_since_change.return_value = self.RECENTLY

        run_thermostat()

        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.FURNACE)
        mock_gpio.turn_on_hvac.assert_not_called()
        self.HVAC.record_change.assert_called_once_with(None)

    def test_run_thermostat__should_start_furnace_when_below_deadband(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 20.4, Automation.HVAC.MODE.HEATING)

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.FURNACE)
        self.HVAC.record_change.assert_called_once_with(Automation.HVAC.FURNACE)

    def test_run_thermostat__should_not_start_furnace_within_deadband(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 20.6, Automation.HVAC.MODE.HEATING)

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_not_start_furnace_before_minimum_off_time(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 18.0, Automation.HVAC.MODE.HEATING)
        self.HVAC.seconds_since_change.return_value = self.RECENTLY

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_keep_furnace_running_until_target_reached(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 20.8, Automation.HVAC.MODE.HEATING)
        self.HVAC.active_device = Automation.HVAC.FURNACE

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()
        mock_gpio.turn_off_hvac.assert_not_called()

    def test_run_thermostat__should_turn_off_furnace_at_target_after_minimum_on_time(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 21.0, Automation.HVAC.MODE.HEATING)
        self.HVAC.active_device = Automation.HVAC.FURNACE

        run_thermostat()

        mock_gpio.turn_off_hvac.assert_called_once_with(Automation.HVAC.FURNACE)
        self.HVAC.record_change.assert_called_once_with(None)

    def test_run_thermostat__should_keep_furnace_running_at_target_before_minimum_on_time(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 21.5, Automation.HVAC.MODE.HEATING)
        self.HVAC.active_device = Automation.HVAC.FURNACE
        self.HVAC.seconds_since_change.return_value = self.RECENTLY

        run_thermostat()

        mock_gpio.turn_off_hvac.assert_not_called()

    def test_run_thermostat__should_start_ac_when_above_deadband(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 22.6, Automation.HVAC.MODE.COOLING, desired_temp=22.0)

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_thermostat__should_not_start_ac_within_deadband(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 22.4, Automation.HVAC.MODE.COOLING, desired_temp=22.0)

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_turn_off_ac_at_target_after_minimum_on_time(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 22.0, Automation.HVAC.MODE.COOLING, desired_temp=22.0)
        self.HVAC.active_device = Automation.HVAC.AIR_CONDITIONING

        run_thermostat()

        mock_gpio.turn_off_hvac.assert_called_once_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_thermostat__should_not_start_furnace_in_cooling_mode(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 10.0, Automation.HVAC.MODE.COOLING, desired_temp=22.0)

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_not_read_schedule_when_not_auto(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 20.0, Automation.HVAC.MODE.HEATING)

        run_thermostat()

        mock_file.get_schedule.assert_not_called()

    def test_run_thermostat__should_heat_toward_active_task_start_temp_when_auto(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 21.0, Automation.HVAC.MODE.AUTO, tasks=[self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.FURNACE)

    def test_run_thermostat__should_use_stop_temp_outside_task_window_when_auto(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 19.0, Automation.HVAC.MODE.AUTO, tasks=[self.TASK], now=self.MONDAY_NIGHT)

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_turn_everything_off_when_auto_and_no_task_today(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.TASK['alarmDays'] = 'TueThu'
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 10.0, Automation.HVAC.MODE.AUTO, tasks=[self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()
        mock_gpio.turn_off_hvac.assert_has_calls([call(Automation.HVAC.AIR_CONDITIONING), call(Automation.HVAC.FURNACE)])

    def test_run_thermostat__should_not_start_anything_within_auto_band(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.TASK['hvacMode'] = Automation.HVAC.MODE.AUTO
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 22.5, Automation.HVAC.MODE.AUTO, tasks=[self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_heat_when_below_auto_band(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.TASK['hvacMode'] = Automation.HVAC.MODE.AUTO
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 20.5, Automation.HVAC.MODE.AUTO, tasks=[self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.FURNACE)

    def test_run_thermostat__should_cool_when_above_auto_band(self, mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac):
        self.TASK['hvacMode'] = Automation.HVAC.MODE.AUTO
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, mock_hvac, 23.5, Automation.HVAC.MODE.AUTO, tasks=[self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.AIR_CONDITIONING)


@patch('svc.services.thermostat_service.HvacState')
@patch('svc.services.thermostat_service.gpio_utils')
class TestStopHvac:

    def test_stop_hvac__should_turn_off_both_relays(self, mock_gpio, mock_hvac):
        mock_hvac.get_instance.return_value = MagicMock(active_device=None)

        stop_hvac()

        mock_gpio.turn_off_hvac.assert_has_calls([call(Automation.HVAC.AIR_CONDITIONING), call(Automation.HVAC.FURNACE)])

    def test_stop_hvac__should_not_reset_change_time_when_nothing_was_running(self, mock_gpio, mock_hvac):
        state = MagicMock(active_device=None)
        mock_hvac.get_instance.return_value = state

        stop_hvac()

        state.record_change.assert_not_called()
