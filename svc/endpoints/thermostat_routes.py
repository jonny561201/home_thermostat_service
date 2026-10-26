from flask import Response, Blueprint
from flask import request

from svc.constants.home_automation import Mime
from svc.controllers import thermostat_controller


THERMOSTAT_BLUEPRINT = Blueprint('thermostat_blueprint', __name__, url_prefix='/thermostat')


@THERMOSTAT_BLUEPRINT.route('/status', methods=['GET'])
def get_thermostat_status():
    api_key = request.headers.get('X-API-Key')
    status = thermostat_controller.get_status(api_key)
    return Response(status.to_json(), status=200, mimetype=Mime.JSON)
