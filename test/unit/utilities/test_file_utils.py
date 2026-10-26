import json
import os
import tempfile

from mock import patch

from svc.constants.home_automation import Hvac
from svc.utilities import file_utils


@patch('svc.utilities.file_utils.Settings')
class TestFileUtils:
    TASKS = [{'taskId': 'task-1', 'alarmDays': 'Mon', 'hvacStart': '06:00:00', 'hvacStop': '22:00:00',
              'hvacStartTemp': 21.0, 'hvacStopTemp': 18.0, 'hvacMode': 'heating'}]

    def setup_method(self):
        self.DIRECTORY = tempfile.mkdtemp()
        self.STATE_FILE = os.path.join(self.DIRECTORY, 'state.json')
        self.SCHEDULE_FILE = os.path.join(self.DIRECTORY, 'schedule.json')

    def __arrange(self, mock_settings):
        mock_settings.get_instance.return_value.state_file = self.STATE_FILE
        mock_settings.get_instance.return_value.schedule_file = self.SCHEDULE_FILE

    def test_get_desired_state__should_return_default_when_file_missing(self, mock_settings):
        self.__arrange(mock_settings)

        actual = file_utils.get_desired_state()

        assert actual == {'desiredTemp': Hvac.DEFAULT_DESIRED_TEMP, 'mode': Hvac.MODE.TURN_OFF}

    def test_get_desired_state__should_create_file_when_missing(self, mock_settings):
        self.__arrange(mock_settings)

        file_utils.get_desired_state()

        with open(self.STATE_FILE) as file:
            assert json.load(file) == {'desiredTemp': Hvac.DEFAULT_DESIRED_TEMP, 'mode': Hvac.MODE.TURN_OFF}

    def test_save_desired_state__should_be_returned_by_get_desired_state(self, mock_settings):
        self.__arrange(mock_settings)

        file_utils.save_desired_state(22.5, 'cooling')

        assert file_utils.get_desired_state() == {'desiredTemp': 22.5, 'mode': 'cooling'}

    def test_get_schedule__should_return_empty_list_when_file_missing(self, mock_settings):
        self.__arrange(mock_settings)

        actual = file_utils.get_schedule()

        assert actual == []

    def test_save_schedule__should_be_returned_by_get_schedule(self, mock_settings):
        self.__arrange(mock_settings)

        file_utils.save_schedule(self.TASKS)

        assert file_utils.get_schedule() == self.TASKS

    def test_save_schedule__should_replace_existing_schedule(self, mock_settings):
        self.__arrange(mock_settings)
        file_utils.save_schedule(self.TASKS)

        file_utils.save_schedule([])

        assert file_utils.get_schedule() == []
