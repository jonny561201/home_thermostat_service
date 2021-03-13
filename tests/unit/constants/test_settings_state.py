import os

from src.constants.settings_state import Settings


class TestState:
    SETTINGS = None
    FILE_NAME = "test.json"
    HUB_BASE_URL = 'http://www.fakeurl.com'

    def setup_method(self):
        os.environ.update({'TEMP_FILE_NAME': self.FILE_NAME, 'HUB_BASE_URL': self.HUB_BASE_URL})
        self.SETTINGS = Settings.get_instance()

    def teardown_method(self):
        os.environ.pop('TEMP_FILE_NAME')
        os.environ.pop('HUB_BASE_URL')

    def test_file_name__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.temp_file_name == self.FILE_NAME

    def test_hub_base_url__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.hub_base_url == self.HUB_BASE_URL

    def test_file_name__should_pull_from_dictionary_if_dev_mode(self):
        file_name = 'other_file_name'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'TempFileName': file_name}
        assert self.SETTINGS.temp_file_name == file_name

    def test_hub_base_url__should_pull_from_dictionary_if_dev_mode(self):
        base_url = 'http://www.other_user_id.com'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'HubBaseUrl': base_url}
        assert self.SETTINGS.hub_base_url == base_url
