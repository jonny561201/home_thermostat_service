import uuid
from datetime import time, datetime

from mock import patch

from src.constants.settings_state import Settings
from src.constants.thread_state import AutoHvacState


@patch('src.constants.thread_state.convert_to_celsius')
@patch('src.constants.thread_state.get_weather_data_by_user')
class TestThreadState:
    BLANK = '00:00:00'
    START = '07:23:00'
    STOP = '08:41:00'
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        Settings.get_instance().settings = {'UserId': self.USER_ID}

    def test_hvac_state__should_convert_start_time_to_time_object(self, mock_api, mock_convert):
        actual = AutoHvacState(None, None, self.START, self.BLANK, None, None)
        assert actual.START_TIME == time(hour=7, minute=23)

    def test_hvac_state__should_convert_stop_time_to_time_object(self, mock_api, mock_convert):
        actual = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        assert actual.STOP_TIME == time(hour=8, minute=41)

    def test_get_daily_high__should_make_api_call_to_get_daily_high_value(self, mock_api, mock_convert):
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)

        state.get_daily_high()

        mock_api.assert_called_with(self.USER_ID)

    def test_get_daily_high__should_return_daily_high_value(self, mock_api, mock_convert):
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        response = {"currentTemp": 73.616, "isFahrenheit": False, "maxTemp": 60.8, "minTemp": 59, "temp": 59.67}
        mock_api.return_value = response

        actual = state.get_daily_high()

        assert actual == response['maxTemp']

    def test_get_daily_high__should_convert_to_celsius_when_fahrenheit(self, mock_api, mock_convert):
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        response = {"currentTemp": 73.616, "isFahrenheit": True, "maxTemp": 60.8, "minTemp": 59, "temp": 59.67}
        mock_api.return_value = response
        celsius_temp = 16.0
        mock_convert.return_value = celsius_temp

        actual = state.get_daily_high()

        assert actual == celsius_temp

    def test_get_daily_high__should_return_cached_value(self, mock_api, mock_convert):
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        cached_temp = 23.0
        state.DAILY_TEMP = cached_temp
        actual = state.get_daily_high()

        assert actual == cached_temp

    @patch('src.constants.thread_state.datetime')
    def test_get_daily_high__should_reset_cached_value_when_rolls_over_to_new_day(self, mock_date, mock_api, mock_convert):
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=0, minute=0)
        response = {"currentTemp": 73.616, "isFahrenheit": False, "maxTemp": 21.3, "minTemp": 59, "temp": 59.67}
        mock_api.return_value = response
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        cached_temp = 23.0
        state.DAILY_TEMP = cached_temp
        state.get_daily_high()

        assert state.DAILY_TEMP == response['maxTemp']

    @patch('src.constants.thread_state.datetime')
    def test_get_daily_high__should_reset_cached_value_when_within_the_first_few_minutes(self, mock_date, mock_api, mock_convert):
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=0, minute=1)
        response = {"currentTemp": 73.616, "isFahrenheit": False, "maxTemp": 21.3, "minTemp": 59, "temp": 59.67}
        mock_api.return_value = response
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        cached_temp = 23.0
        state.DAILY_TEMP = cached_temp
        state.get_daily_high()

        assert state.DAILY_TEMP == response['maxTemp']

    @patch('src.constants.thread_state.datetime')
    def test_get_daily_high__should_store_cached_daily_value_when_celsius(self, mock_date, mock_api, mock_convert):
        response = {"currentTemp": 73.616, "isFahrenheit": False, "maxTemp": 22.0, "minTemp": 59, "temp": 59.67}
        mock_api.return_value = response
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=0, minute=1)
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        state.get_daily_high()

        assert state.DAILY_TEMP == response['maxTemp']

    @patch('src.constants.thread_state.datetime')
    def test_get_daily_high__should_store_cached_daily_value_when_fahrenheit(self, mock_date, mock_api, mock_convert):
        response = {"currentTemp": 73.616, "isFahrenheit": True, "maxTemp": 60.8, "minTemp": 59, "temp": 59.67}
        mock_api.return_value = response
        celsius_value = 16.0
        mock_convert.return_value = celsius_value
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=0, minute=1)
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        state.get_daily_high()

        assert state.DAILY_TEMP == celsius_value

    @patch('src.constants.thread_state.datetime')
    def test_get_daily_high__when_api_call_fails_return_none_and_reset_daily_temp(self, mock_date, mock_api, mock_convert):
        mock_api.return_value = None
        mock_date.now.return_value = datetime(year=2021, month=2, day=15, hour=0, minute=1)
        state = AutoHvacState(None, None, self.BLANK, self.STOP, None, None)
        actual = state.get_daily_high()

        assert state.DAILY_TEMP is None
        assert actual is None
