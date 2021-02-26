from mock import patch, ANY

from src.services.temperature_service import get_internal_temp


@patch('src.services.temperature_service.get_user_temperature')
@patch('src.services.temperature_service.read_temperature_file')
class TestTemperatureService:
    PREFERENCES = None
    CITY = 'London'
    UNIT = 'celsius'
    APP_ID = 'fake app id'

    def setup_method(self):
        self.PREFERENCES = {'city': self.CITY, 'temp_unit': self.UNIT, 'is_fahrenheit': True}

    def test_get_internal_temp__should_call_read_temperature_file(self, mock_file, mock_temp):
        get_internal_temp(self.PREFERENCES)

        mock_file.assert_called()

    def test_get_internal_temp__should_call_get_user_temperature_with_text_results(self, mock_file, mock_temp):
        temp_text = "2324.455"
        mock_file.return_value = temp_text
        get_internal_temp(self.PREFERENCES)

        mock_temp.assert_called_with(temp_text, ANY)

    def test_get_internal_temp__should_call_get_user_temperature_with_preference_fahrenheit(self, mock_file, mock_temp):
        get_internal_temp(self.PREFERENCES)

        mock_temp.assert_called_with(ANY, self.PREFERENCES['is_fahrenheit'])
