import pytest
from mock import patch
from werkzeug.exceptions import Unauthorized

from svc.controllers.thermostat_controller import get_status


@patch('svc.controllers.thermostat_controller.file_utils')
@patch('svc.controllers.thermostat_controller.validate_api_key')
@patch('svc.controllers.thermostat_controller.gpio_utils')
class TestThermostatController:
    API_KEY = 'fake_api_key'
    TEMP_TEXT = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES', '72 01 4b 46 7f ff 0e 10 57 t=21500']
    STATE = {'desiredTemp': 22.0, 'mode': 'heating'}

    def test_get_status__should_validate_api_key(self, mock_gpio, mock_validate, mock_file):
        mock_gpio.read_temperature_file.return_value = self.TEMP_TEXT
        mock_file.get_desired_state.return_value = self.STATE

        get_status(self.API_KEY)

        mock_validate.assert_called_with(self.API_KEY)

    def test_get_status__should_raise_unauthorized_when_api_key_invalid(self, mock_gpio, mock_validate, mock_file):
        mock_validate.side_effect = Unauthorized()

        with pytest.raises(Unauthorized):
            get_status(self.API_KEY)

        mock_gpio.read_temperature_file.assert_not_called()

    def test_get_status__should_return_current_temp_in_celsius(self, mock_gpio, mock_validate, mock_file):
        mock_gpio.read_temperature_file.return_value = self.TEMP_TEXT
        mock_file.get_desired_state.return_value = self.STATE

        actual = get_status(self.API_KEY)

        assert actual.currentTemp == 21.5

    def test_get_status__should_return_none_current_temp_when_sensor_unavailable(self, mock_gpio, mock_validate, mock_file):
        mock_gpio.read_temperature_file.return_value = []
        mock_file.get_desired_state.return_value = self.STATE

        actual = get_status(self.API_KEY)

        assert actual.currentTemp is None

    def test_get_status__should_return_desired_temp_and_mode(self, mock_gpio, mock_validate, mock_file):
        mock_gpio.read_temperature_file.return_value = self.TEMP_TEXT
        mock_file.get_desired_state.return_value = self.STATE

        actual = get_status(self.API_KEY)

        assert actual.desiredTemp == 22.0
        assert actual.mode == 'heating'
