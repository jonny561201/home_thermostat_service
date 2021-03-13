import json
import os
from datetime import time

from mock import patch
from requests import Response
from src.constants.settings_state import Settings
from src.utilities.api_utils import get_hvac_tasks_by_user


@patch('src.utilities.api_utils.requests')
class TestLightApiRequests:
    USER_ID = 'def456'
    BASE_URL = 'http://hubbaseurl.com'

    def setup_method(self):
        self.SETTINGS = Settings.get_instance().dev_mode = False
        os.environ.update({'HUB_BASE_URL': self.BASE_URL})

    def teardown_method(self):
        os.environ.pop('HUB_BASE_URL')

    def test_get_hvac_tasks_by_user__should_make_rest_call_using_url(self, mock_requests):
        get_hvac_tasks_by_user(self.USER_ID)

        mock_requests.get.assert_called_with(f'{self.BASE_URL}/userId/{self.USER_ID}/tasks', timeout=5)

    def test_get_hvac_tasks_by_user__should_return_response(self, mock_requests):
        response = [{'alarm_light_group': '1', 'alarm_time': None}]
        mock_requests.get.return_value = self.__create_response(status=200, data=response)
        actual = get_hvac_tasks_by_user(self.USER_ID)

        assert actual == response

    def test_get_hvac_tasks_by_user__should_convert_alarm_time_to_time_object(self, mock_requests):
        response = [{'alarm_light_group': '1', 'alarm_time': '00:00:01'}]
        mock_requests.get.return_value = self.__create_response(status=200, data=response)
        actual = get_hvac_tasks_by_user(self.USER_ID)

        assert actual[0]['alarm_time'] == time(hour=0, minute=0, second=1)

    def test_get_hvac_tasks_by_user__should_return_empty_list_when_alarm_is_not_present(self, mock_requests):
        response = []
        mock_requests.get.return_value = self.__create_response(status=200, data=response)
        actual = get_hvac_tasks_by_user(self.USER_ID)

        assert actual == []

    def test_get_hvac_tasks_by_user__should_return_none_when_response_throws_exception(self, mock_requests):
        mock_requests.get.side_effect = TimeoutError()
        actual = get_hvac_tasks_by_user(self.USER_ID)

        assert actual is None

    @staticmethod
    def __create_response(status=200, data=None):
        response = Response()
        response.status_code = status
        response._content = json.dumps(data).encode('UTF-8')
        return response
