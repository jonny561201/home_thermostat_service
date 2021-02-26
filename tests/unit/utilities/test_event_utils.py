from threading import Event

from mock import patch, Mock, ANY

from src.constants.home_automation import Automation
from src.utilities.event_utils import create_thread


def my_function(*args):
    pass


@patch('src.utilities.event_utils.Event')
class TestEvent:
    FUNCT = my_function

    def test_create_thread__should_set_stop_event(self, mock_event):
        event = Event()
        mock_event.return_value = event
        actual = create_thread(self.FUNCT)

        assert actual.stopped == event

    @patch('src.utilities.event_utils.MyThread')
    def test_create_thread__should_return_thread(self, mock_thread, mock_event):
        thread = Mock()
        mock_thread.return_value = thread
        actual = create_thread(self.FUNCT)

        assert actual == thread

    @patch('src.utilities.event_utils.MyThread')
    def test_create_thread__should_create_thread_with_stop_event(self, mock_thread, mock_event):
        event = Mock()
        mock_event.return_value = event
        create_thread(self.FUNCT)

        mock_thread.assert_called_with(event, ANY, ANY)

    @patch('src.utilities.event_utils.MyThread')
    def test_create_thread__should_create_thread_with_provided_function(self, mock_thread, mock_event):
        create_thread(self.FUNCT)

        mock_thread.assert_called_with(ANY, self.FUNCT, ANY)

    @patch('src.utilities.event_utils.MyThread')
    def test_create_thread__should_create_thread_with_default_delay(self, mock_thread, mock_event):
        create_thread(self.FUNCT)

        mock_thread.assert_called_with(ANY, ANY, Automation.TIME.THIRTY_SECONDS)

    @patch('src.utilities.event_utils.MyThread')
    def test_create_thread__should_create_thread_with_overridden_delay_value(self, mock_thread, mock_event):
        create_thread(self.FUNCT, Automation.TIME.TEN_MINUTE)

        mock_thread.assert_called_with(ANY, ANY, Automation.TIME.TEN_MINUTE)
