import logging

from src.constants.home_automation import Automation
from src.services.thermostat_service import run_thermostat_program
from src.utilities.event_utils import create_thread

logging.basicConfig(filename='thermostat.log', level=logging.INFO)

try:
    logging.info('Application started!')
    thread = create_thread(run_thermostat_program, Automation.TIME.ONE_MINUTE)
    thread.start()
except Exception:
    logging.error('Application interrupted by user')
