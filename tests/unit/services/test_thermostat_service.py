import uuid
from datetime import time, datetime

from mock import patch, ANY, call, mock

from src.constants.home_automation import Automation
from src.constants.thread_state import AutoHvacState
from src.services.thermostat_service import run_auto_thermostat_program, run_manual_thermostat_program


@patch('src.services.thermostat_service.get_desired_temp')
@patch('src.services.thermostat_service.gpio_utils')
@patch('src.services.thermostat_service.get_user_temperature')
class TestManualHvac:
    DESIRED_TEMP = 33.0
    AC_TEMP = 35.0
    HEAT_TEMP = 31.0
    TASK_ID = str(uuid.uuid4())

    def setup_method(self):
        self.FILE_DESIRED = {'desiredTemp': self.DESIRED_TEMP, 'mode': Automation.HVAC.MODE.COOLING, 'isAuto': False}

    def test_run_temperature_program__should_not_read_temp_file_when_not_in_manual_mode(self, mock_convert, mock_gpio, mock_file):
        self.FILE_DESIRED['mode'] = None
        mock_file.return_value = self.FILE_DESIRED
        run_manual_thermostat_program()
        mock_gpio.read_temperature_file.assert_not_called()

    def test_run_temperature_program__should_turn_everything_off_when_not_auto_and_not_manual_mode(self, mock_convert, mock_gpio, mock_file):
        self.FILE_DESIRED['mode'] = None
        mock_file.return_value = self.FILE_DESIRED
        run_manual_thermostat_program()
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.FURNACE)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.AIR_CONDITIONING)

    def test_run_temperature_program__should_stop_if_temp_file_returns_none(self, mock_convert, mock_gpio, mock_file):
        mock_gpio.read_temperature_file.return_value = None
        run_manual_thermostat_program()
        mock_convert.assert_not_called()

    def test_run_temperature_program__should_not_turn_everything_off_when_auto_mode(self, mock_convert, mock_gpio, mock_file):
        self.FILE_DESIRED['mode'] = None
        self.FILE_DESIRED['isAuto'] = True
        mock_file.return_value = self.FILE_DESIRED
        run_manual_thermostat_program()
        mock_gpio.turn_off_hvac.assert_not_called()
        mock_gpio.turn_off_hvac.assert_not_called()

    def test_run_temperature_program__should_make_call_to_read_temperature_file(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.AC_TEMP
        run_manual_thermostat_program()
        mock_gpio.read_temperature_file.assert_called()

    def test_run_temperature_program__should_call_get_user_temperature(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_gpio.read_temperature_file.return_value = self.AC_TEMP
        mock_convert.return_value = self.AC_TEMP

        run_manual_thermostat_program()
        mock_convert.assert_called()

    def test_run_temperature_program__should_make_call_to_get_user_temperature_with_result_of_temp_file(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_gpio.read_temperature_file.return_value = self.AC_TEMP
        mock_convert.return_value = self.AC_TEMP

        run_manual_thermostat_program()
        mock_convert.assert_called_with(self.AC_TEMP, ANY)

    def test_run_temperature_program__should_make_call_to_get_user_temperature_with_celsius(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.AC_TEMP

        run_manual_thermostat_program()
        mock_convert.assert_called_with(ANY, False)

    def test_run_temperature_program__should_not_call_ac_on_when_temp_below_desired(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.HEAT_TEMP

        run_manual_thermostat_program()
        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_temperature_program__should_turn_on_ac_when_temp_above_desired_and_mode_cooling(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.AC_TEMP

        run_manual_thermostat_program()
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_temperature_program__should_turn_on_furnace_when_temp_below_desired_and_mode_heating(self, mock_convert, mock_gpio, mock_file):
        self.FILE_DESIRED['mode'] = Automation.HVAC.MODE.HEATING
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.HEAT_TEMP

        run_manual_thermostat_program()
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_temperature_program__should_not_turn_on_furnace_when_temp_above_desired_and_mode_heating(self, mock_convert, mock_gpio, mock_file):
        self.FILE_DESIRED['mode'] = Automation.HVAC.MODE.HEATING
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.AC_TEMP

        run_manual_thermostat_program()
        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_temperature_program__should_turn_off_furnace_when_temp_above_desired_and_mode_heating(self, mock_convert, mock_gpio, mock_file):
        self.FILE_DESIRED['mode'] = Automation.HVAC.MODE.HEATING
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.AC_TEMP

        run_manual_thermostat_program()
        mock_gpio.turn_off_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_temperature_program__should_turn_off_furnace_when_temp_equal_desired_and_mode_heating(self, mock_convert, mock_gpio, mock_file):
        self.FILE_DESIRED['mode'] = Automation.HVAC.MODE.HEATING
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.DESIRED_TEMP

        run_manual_thermostat_program()
        mock_gpio.turn_off_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_temperature_program__should_turn_off_ac_and_furnace_when_temp_below_desired_and_mode_cooling(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.HEAT_TEMP
        mock_call_1 = call(Automation.HVAC.AIR_CONDITIONING)
        mock_call_2 = call(Automation.HVAC.FURNACE)

        run_manual_thermostat_program()
        mock_gpio.turn_off_hvac.assert_has_calls([mock_call_1, mock_call_2])

    def test_run_temperature_program__should_turn_off_ac_and_furnace_when_temp_equal_desired_and_mode_heating(self, mock_convert, mock_gpio, mock_file):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = self.DESIRED_TEMP
        mock_call_1 = call(Automation.HVAC.AIR_CONDITIONING)
        mock_call_2 = call(Automation.HVAC.FURNACE)

        run_manual_thermostat_program()
        mock_gpio.turn_off_hvac.assert_has_calls([mock_call_1, mock_call_2])


@patch('src.constants.thread_state.get_weather_data_by_user')
@patch('src.services.thermostat_service.datetime')
@patch('src.services.thermostat_service.get_desired_temp')
@patch('src.services.thermostat_service.gpio_utils')
@patch('src.services.thermostat_service.get_user_temperature')
class TestAutomaticHvac:
    AC_TEMP = 35.0
    HEAT_TEMP = 31.0
    DESIRED_TEMP = 33.0
    TASK_DAYS = 'MonTue'
    START_TEMP = 23
    STOP_TEMP = 17
    START_TIME = '07:00:00'
    STOP_TIME = '22:00:00'
    TASK_ID = str(uuid.uuid4())

    def setup_method(self):
        self.FILE_DESIRED = {'desiredTemp': self.DESIRED_TEMP, 'mode': None, 'isAuto': True}

    def test_run_auto_temperature_program__should_not_read_temp_file_when_not_auto_mode(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        self.FILE_DESIRED['isAuto'] = False
        mock_file.return_value = self.FILE_DESIRED

        run_auto_thermostat_program(None)
        mock_gpio.read_temperature_file.assert_not_called()

    def test_run_auto_temperature_program__should_stop_program_when_temp_file_returns_none(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_date.now.return_value = datetime(year=2021, month=2, day=17, hour=8)
        mock_gpio.read_temperature_file.return_value = None
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        run_auto_thermostat_program(state)

        mock_convert.assert_not_called()

    def test_run_auto_temperature_program__should_make_call_to_get_daily_high(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 20
        mock_state = mock.create_autospec(AutoHvacState)
        mock_state.DAYS = self.TASK_DAYS
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=8)
        mock_state.START_TIME = time.fromisoformat(self.START_TIME)
        mock_state.STOP_TIME = time.fromisoformat(self.STOP_TIME)
        mock_state.get_daily_high.return_value = 22

        run_auto_thermostat_program(mock_state)
        mock_state.get_daily_high.assert_called()

    def test_run_auto_temperature_program__when_cooling_outside_selected_days_will_not_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_date.now.return_value = datetime(year=2021, month=2, day=17, hour=8)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_auto_temperature_program__when_in_cooling_mode_temp_above_cooling_threshold_and_between_start_stop_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 25
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=8)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_auto_temperature_program__when_in_cooling_mode_temp_above_cooling_threshold_and_at_start_time_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 25
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=7, minute=00, second=00)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_auto_temperature_program__when_in_cooling_mode_temp_below_cooling_threshold_and_at_start_time_will_turn_off_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 22
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=7, minute=00, second=00)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.AIR_CONDITIONING)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_in_heating_mode_temp_below_heating_threshold_and_at_start_time_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 17
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=7)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.STOP_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_in_heating_mode_temp_below_heating_threshold_and_between_start_stop_time_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 17
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=8)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.STOP_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_in_heating_mode_temp_above_heating_threshold_and_at_start_time_will_turn_off_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 24
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=8)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.STOP_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.AIR_CONDITIONING)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_in_heating_mode_temp_below_heating_threshold_and_before_time_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 16
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=6, minute=59)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.STOP_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_in_heating_mode_temp_below_heating_threshold_and_after_time_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 16
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=22, minute=1)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.STOP_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_in_cooling_mode_temp_above_cooling_threshold_and_before_time_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 20
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=6, minute=59)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_auto_temperature_program__when_in_cooling_mode_temp_above_cooling_threshold_and_after_time_will_turn_on_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 19
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=22, minute=1)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_auto_temperature_program__when_in_cooling_mode_temp_below_heating_threshold_and_during_time_will_not_turn_on_cooling(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = Automation.HVAC.MIN_COOLING + 1
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=18)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_not_called()

    def test_run_auto_temperature_program__when_below_min_cooling_will_flip_to_heating_mode(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = Automation.HVAC.MIN_COOLING - 1
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=18)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_at_min_cooling_will_flip_to_heating_mode(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = Automation.HVAC.MIN_COOLING
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=18)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_above_max_heating_will_flip_to_cooling_mode(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = Automation.HVAC.MAX_HEATING + 1
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=18)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = 21

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_auto_temperature_program__when_at_max_heating_will_flip_to_cooling_mode(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = Automation.HVAC.MAX_HEATING
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=18)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = 21

        run_auto_thermostat_program(state)
        mock_gpio.turn_on_hvac.assert_called_with(Automation.HVAC.AIR_CONDITIONING)

    def test_run_auto_temperature_program__when_in_heating_mode_temp_above_heating_threshold_and_before_time_will_turn_off_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 18
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=6, minute=59)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.STOP_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.AIR_CONDITIONING)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.FURNACE)

    def test_run_auto_temperature_program__when_in_cooling_mode_temp_below_cooling_threshold_and_after_time_will_turn_off_hvac(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 16
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=22, minute=1)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)
        state.DAILY_TEMP = self.START_TEMP

        run_auto_thermostat_program(state)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.AIR_CONDITIONING)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.FURNACE)


    def test_run_auto_temperature_program__should_turn_off_hvac_when_daily_high_fails(self, mock_convert, mock_gpio, mock_file, mock_date, mock_api):
        mock_api.return_value = None
        mock_file.return_value = self.FILE_DESIRED
        mock_convert.return_value = 19
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=22, minute=1)
        state = AutoHvacState(self.TASK_ID, self.TASK_DAYS, self.START_TIME, self.STOP_TIME, self.START_TEMP, self.STOP_TEMP)

        run_auto_thermostat_program(state)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.AIR_CONDITIONING)
        mock_gpio.turn_off_hvac.assert_any_call(Automation.HVAC.FURNACE)
