from datetime import time

from src.constants.thread_state import HvacState


def test_hvac_state__should_convert_start_time_to_time_object():
    start = '07:23:00'
    stop = '00:00:00'
    actual = HvacState(None, None, start, stop, None, None)
    assert actual.START_TIME == time(hour=7, minute=23)


def test_hvac_state__should_convert_stop_time_to_time_object():
    start = '00:00:00'
    stop = '08:41:00'
    actual = HvacState(None, None, start, stop, None, None)
    assert actual.STOP_TIME == time(hour=8, minute=41)