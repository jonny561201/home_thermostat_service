from mock import patch

from svc.utilities.hvac_watcher import start_hvac_watcher


@patch('svc.utilities.hvac_watcher.threading.Thread')
def test_start_hvac_watcher__should_start_daemon_thread(mock_thread):
    start_hvac_watcher()

    assert mock_thread.call_args.kwargs['daemon'] is True
    mock_thread.return_value.start.assert_called_once()
