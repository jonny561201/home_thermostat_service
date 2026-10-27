import time

from svc.config.singleton import Singleton


@Singleton
class HvacState:
    def __init__(self):
        self.active_device = None
        self._last_changed = time.monotonic()

    def record_change(self, device):
        self.active_device = device
        self._last_changed = time.monotonic()

    def seconds_since_change(self):
        return time.monotonic() - self._last_changed
