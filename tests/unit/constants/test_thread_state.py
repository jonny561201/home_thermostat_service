import uuid
from datetime import time

from mock import patch

from src.constants.settings_state import Settings
from src.constants.thread_state import HvacState


class TestThreadState:
    BLANK = '00:00:00'
    START = '07:23:00'
    STOP = '08:41:00'
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        Settings.get_instance().settings = {'UserId': self.USER_ID}

    def test_hvac_state__should_convert_start_time_to_time_object(self):
        actual = HvacState(None, None, self.START, self.BLANK, None, None)
        assert actual.START_TIME == time(hour=7, minute=23)

    def test_hvac_state__should_convert_stop_time_to_time_object(self):
        actual = HvacState(None, None, self.BLANK, self.STOP, None, None)
        assert actual.STOP_TIME == time(hour=8, minute=41)

    @patch('src.constants.thread_state.get_weather_data_by_user')
    def test_get_daily_high__should_make_api_call_to_get_daily_high_value(self, mock_api):
        state = HvacState(None, None, self.BLANK, self.STOP, None, None)

        state.get_daily_high()

        mock_api.assert_called_with(self.USER_ID)

    @patch('src.constants.thread_state.get_weather_data_by_user')
    def test_get_daily_high__should_return_daily_high_value(self, mock_api):
        state = HvacState(None, None, self.BLANK, self.STOP, None, None)
        response = {"currentTemp": 73.616, "isFahrenheit": False, "maxTemp": 60.8, "minTemp": 59, "temp": 59.67}
        mock_api.return_value = response

        actual = state.get_daily_high()

        assert actual == response['maxTemp']