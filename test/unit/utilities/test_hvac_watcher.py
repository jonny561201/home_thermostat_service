import pytest
from mock import call, patch

from svc.utilities.hvac_watcher import start_hvac_watcher, _watch_hvac


@patch('svc.utilities.hvac_watcher.threading.Thread')
def test_start_hvac_watcher__should_start_daemon_thread(mock_thread):
    start_hvac_watcher()

    assert mock_thread.call_args.kwargs['daemon'] is True
    mock_thread.return_value.start.assert_called_once()


@patch('svc.utilities.hvac_watcher.time')
@patch('svc.utilities.hvac_watcher.thermostat_service')
def test_watch_hvac__should_stop_hvac_before_first_run(mock_service, mock_time):
    mock_time.sleep.side_effect = StopIteration

    with pytest.raises(StopIteration):
        _watch_hvac()

    assert mock_service.method_calls == [call.stop_hvac(), call.run_thermostat()]
