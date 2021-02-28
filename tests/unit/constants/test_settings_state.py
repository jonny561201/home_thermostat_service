import os

from src.constants.settings_state import Settings


class TestState:
    SETTINGS = None
    FILE_NAME = "test.json"

    def setup_method(self):
        os.environ.update({'TEMP_FILE_NAME': self.FILE_NAME})
        self.SETTINGS = Settings.get_instance()

    def teardown_method(self):
        os.environ.pop('TEMP_FILE_NAME')

    def test_file_name__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.temp_file_name == self.FILE_NAME

    def test_file_name__should_pull_from_dictionary_if_dev_mode(self):
        file_name = 'other_file_name'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'TempFileName': file_name}
        assert self.SETTINGS.temp_file_name == file_name
