from mock import patch

from svc.config.hvac_state import HvacState
from svc.constants.home_automation import Automation


@patch('svc.config.hvac_state.time')
class TestHvacState:

    def test_hvac_state__should_start_with_nothing_running(self, mock_time):
        mock_time.monotonic.return_value = 100.0

        state = HvacState._decorated()

        assert state.active_device is None

    def test_seconds_since_change__should_count_from_startup(self, mock_time):
        mock_time.monotonic.side_effect = [100.0, 130.0]
        state = HvacState._decorated()

        assert state.seconds_since_change() == 30.0

    def test_record_change__should_set_device_and_reset_timer(self, mock_time):
        mock_time.monotonic.side_effect = [100.0, 500.0, 520.0]
        state = HvacState._decorated()

        state.record_change(Automation.HVAC.FURNACE)

        assert state.active_device == Automation.HVAC.FURNACE
        assert state.seconds_since_change() == 20.0
