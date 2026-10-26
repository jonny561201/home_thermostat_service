from datetime import datetime

from mock import patch, call

from svc.constants.home_automation import Automation
from svc.services.thermostat_service import run_thermostat


@patch('svc.services.thermostat_service.datetime')
@patch('svc.services.thermostat_service.file_utils')
@patch('svc.services.thermostat_service.gpio_utils')
@patch('svc.services.thermostat_service.get_user_temperature')
class TestRunThermostat:
    TEMP_TEXT = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES', '72 01 4b 46 7f ff 0e 10 57 t=21000']
    MONDAY_NOON = datetime(2026, 10, 26, 12, 0, 0)
    MONDAY_NIGHT = datetime(2026, 10, 26, 23, 0, 0)

    def setup_method(self):
        self.TASK = {'taskId': 'task-1', 'alarmDays': 'MonWed', 'hvacStart': '06:00:00', 'hvacStop': '22:00:00',
                     'hvacStartTemp': 22.0, 'hvacStopTemp': 18.0, 'hvacMode': Automation.HVAC.MODE.HEATING}

    def __arrange(self, mock_temp, mock_gpio, mock_file, mock_datetime, current_temp, state, tasks=None, now=None):
        mock_gpio.read_temperature_file.return_value = self.TEMP_TEXT
        mock_temp.return_value = current_temp
        mock_file.get_desired_state.return_value = state
        mock_file.get_schedule.return_value = tasks if tasks is not None else []
        mock_datetime.now.return_value = now if now is not None else self.MONDAY_NOON

    def test_run_thermostat__should_not_touch_relays_when_sensor_reading_missing(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        mock_gpio.read_temperature_file.return_value = []
        mock_temp.return_value = None

        run_thermostat()

        mock_file.get_desired_state.assert_not_called()
        mock_gpio.turn_on_hvac.assert_not_called()
        mock_gpio.turn_off_hvac.assert_not_called()

    def test_run_thermostat__should_read_temperature_in_celsius(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 20.0, {'desiredTemp': 21.0, 'mode': Automation.HVAC.MODE.TURN_OFF})

        run_thermostat()

        mock_temp.assert_called_once_with(self.TEMP_TEXT, False)

    def test_run_thermostat__should_turn_on_furnace_when_heating_and_below_desired(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 20.0, {'desiredTemp': 21.0, 'mode': Automation.HVAC.MODE.HEATING})

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.FURNACE)
        mock_gpio.turn_off_hvac.assert_called_once_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_thermostat__should_turn_all_off_when_heating_and_above_desired(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 22.0, {'desiredTemp': 21.0, 'mode': Automation.HVAC.MODE.HEATING})

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()
        mock_gpio.turn_off_hvac.assert_has_calls([call(Automation.HVAC.AIR_CONDITIONING), call(Automation.HVAC.FURNACE)])

    def test_run_thermostat__should_turn_on_ac_when_cooling_and_above_desired(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 25.0, {'desiredTemp': 22.0, 'mode': Automation.HVAC.MODE.COOLING})

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.AIR_CONDITIONING)
        mock_gpio.turn_off_hvac.assert_called_once_with(Automation.HVAC.FURNACE)

    def test_run_thermostat__should_turn_all_off_when_mode_off(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 15.0, {'desiredTemp': 21.0, 'mode': Automation.HVAC.MODE.TURN_OFF})

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()
        mock_gpio.turn_off_hvac.assert_has_calls([call(Automation.HVAC.AIR_CONDITIONING), call(Automation.HVAC.FURNACE)])

    def test_run_thermostat__should_not_read_schedule_when_not_auto(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 20.0, {'desiredTemp': 21.0, 'mode': Automation.HVAC.MODE.HEATING})

        run_thermostat()

        mock_file.get_schedule.assert_not_called()

    def test_run_thermostat__should_use_start_temp_of_active_task_when_auto(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 21.0, {'desiredTemp': 15.0, 'mode': Automation.HVAC.MODE.AUTO}, [self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.FURNACE)

    def test_run_thermostat__should_use_stop_temp_outside_task_window_when_auto(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 19.0, {'desiredTemp': 15.0, 'mode': Automation.HVAC.MODE.AUTO}, [self.TASK], self.MONDAY_NIGHT)

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_turn_all_off_when_auto_and_no_task_today(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.TASK['alarmDays'] = 'TueThu'
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 10.0, {'desiredTemp': 21.0, 'mode': Automation.HVAC.MODE.AUTO}, [self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()
        mock_gpio.turn_off_hvac.assert_has_calls([call(Automation.HVAC.AIR_CONDITIONING), call(Automation.HVAC.FURNACE)])

    def test_run_thermostat__should_turn_all_off_when_auto_task_within_band(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.TASK['hvacMode'] = Automation.HVAC.MODE.AUTO
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 22.5, {'desiredTemp': 15.0, 'mode': Automation.HVAC.MODE.AUTO}, [self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_thermostat__should_heat_when_auto_task_below_band(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.TASK['hvacMode'] = Automation.HVAC.MODE.AUTO
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 20.5, {'desiredTemp': 15.0, 'mode': Automation.HVAC.MODE.AUTO}, [self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.FURNACE)

    def test_run_thermostat__should_cool_when_auto_task_above_band(self, mock_temp, mock_gpio, mock_file, mock_datetime):
        self.TASK['hvacMode'] = Automation.HVAC.MODE.AUTO
        self.__arrange(mock_temp, mock_gpio, mock_file, mock_datetime, 23.5, {'desiredTemp': 15.0, 'mode': Automation.HVAC.MODE.AUTO}, [self.TASK])

        run_thermostat()

        mock_gpio.turn_on_hvac.assert_called_once_with(Automation.HVAC.AIR_CONDITIONING)
