import json
import os


class Settings:
    __instance = None
    settings = None
    dev_mode = False

    def __init__(self):
        if Settings.__instance is not None:
            raise Exception
        else:
            Settings.__instance = self
            Settings.__instance.__get_settings()

    @property
    def temp_file_name(self):
        return self.settings.get('TempFileName') if self.dev_mode else os.environ.get('TEMP_FILE_NAME')

    @property
    def hub_base_url(self):
        return self.settings.get('HubBaseUrl') if self.dev_mode else os.environ.get('HUB_BASE_URL')

    @property
    def user_id(self):
        return self.settings.get('UserId') if self.dev_mode else os.environ.get('USER_ID')

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings.__instance = Settings()
        return Settings.__instance

    def __get_settings(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            with open(file_path, "r") as reader:
                self.settings = json.loads(reader.read())
                self.dev_mode = self.settings.get("Development", False)
        except Exception:
            self.settings = {}
