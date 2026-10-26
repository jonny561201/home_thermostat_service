import threading
import time

from svc.constants.home_automation import Hvac
from svc.services import thermostat_service


def start_hvac_watcher():
    thread = threading.Thread(target=_watch_hvac, daemon=True)
    thread.start()


def _watch_hvac():
    while True:
        thermostat_service.run_thermostat()
        time.sleep(Hvac.WATCH_INTERVAL_SECONDS)
