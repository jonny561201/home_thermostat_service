from flask import json
from mock import patch

from svc.manager import create_app


FAKE_API_KEY = 'fake_test_api_key_1234567890'


@patch('svc.controllers.thermostat_controller.gpio_utils')
@patch('svc.controllers.thermostat_controller.file_utils')
@patch('svc.utilities.api_key_utils.get_api_key', return_value=FAKE_API_KEY)
class TestThermostatRoutesIntegration:

    def setup_method(self):
        self.HEADERS = {'X-API-Key': FAKE_API_KEY}
        self.APP = create_app()
        self.TEST_CLIENT = self.APP.test_client()

    def test_get_thermostat_status__should_return_unauthorized_with_no_header(self, mock_key, mock_file, mock_gpio):
        actual = self.TEST_CLIENT.get('thermostat/status')

        assert actual.status_code == 401

    def test_get_thermostat_status__should_return_unauthorized_with_invalid_api_key(self, mock_key, mock_file, mock_gpio):
        actual = self.TEST_CLIENT.get('thermostat/status', headers={'X-API-Key': 'bad_key'})

        assert actual.status_code == 401

    def test_get_thermostat_status__should_return_status_json(self, mock_key, mock_file, mock_gpio):
        mock_gpio.read_temperature_file.return_value = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES', '72 01 4b 46 7f ff 0e 10 57 t=21500']
        mock_file.get_desired_state.return_value = {'desiredTemp': 22.0, 'mode': 'heating'}

        actual = self.TEST_CLIENT.get('thermostat/status', headers=self.HEADERS)

        assert actual.status_code == 200
        assert actual.mimetype == 'application/json'
        assert json.loads(actual.data) == {'currentTemp': 21.5, 'desiredTemp': 22.0, 'mode': 'heating'}
