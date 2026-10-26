from svc.models.status import ThermostatStatus
from svc.utilities import file_utils
from svc.utilities import gpio_utils
from svc.utilities.api_key_utils import validate_api_key
from svc.utilities.user_temp_utils import get_user_temperature


def get_status(api_key):
    validate_api_key(api_key)
    current_temp = get_user_temperature(gpio_utils.read_temperature_file(), False)
    state = file_utils.get_desired_state()

    return ThermostatStatus(currentTemp=current_temp, desiredTemp=state['desiredTemp'], mode=state['mode'])
