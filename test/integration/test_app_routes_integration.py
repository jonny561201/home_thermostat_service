from svc.manager import create_app


class TestAppRoutesIntegration:

    def setup_method(self):
        self.APP = create_app()
        self.TEST_CLIENT = self.APP.test_client()

    def test_get_health__should_return_success(self):
        actual = self.TEST_CLIENT.get('/health')

        assert actual.status_code == 200
