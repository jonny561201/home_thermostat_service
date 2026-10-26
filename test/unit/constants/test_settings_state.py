from svc.config.settings_state import Settings


class TestSettingsState:
    VALUES = {'StateFile': 'other_state.json', 'ScheduleFile': 'other_schedule.json', 'Environment': 'test'}
    QUEUE = {'Host': 'test_host', 'Port': 1234, 'VHost': 'test_vhost', 'Exchange': 'test_exchange'}

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS._settings = self.VALUES
        self.SETTINGS.Queue._settings = self.QUEUE

    def test_environment__should_return(self):
        assert self.SETTINGS.environment == self.VALUES['Environment']

    def test_environment__should_default_to_local(self):
        self.SETTINGS._settings = None
        assert self.SETTINGS.environment == 'local'

    def test_state_file__should_return(self):
        assert self.SETTINGS.state_file == self.VALUES['StateFile']

    def test_state_file__should_provide_default(self):
        self.SETTINGS._settings = None
        assert self.SETTINGS.state_file == 'thermostatState.json'

    def test_schedule_file__should_return(self):
        assert self.SETTINGS.schedule_file == self.VALUES['ScheduleFile']

    def test_schedule_file__should_provide_default(self):
        self.SETTINGS._settings = None
        assert self.SETTINGS.schedule_file == 'thermostatSchedule.json'

    def test_queue_host__should_return(self):
        assert self.SETTINGS.Queue.host == self.QUEUE['Host']

    def test_queue_vhost__should_return(self):
        assert self.SETTINGS.Queue.vhost == self.QUEUE['VHost']

    def test_queue_port__should_return(self):
        assert self.SETTINGS.Queue.port == self.QUEUE['Port']

    def test_queue_exchange__should_return(self):
        assert self.SETTINGS.Queue.exchange == self.QUEUE['Exchange']
