import json

from svc.utilities import file_utils


def update_hvac_worker(ch, method, properties, body: bytes):
    try:
        request = json.loads(body)
        action = request.get('action')

        if action == 'set':
            file_utils.save_desired_state(request['desiredTemp'], request['mode'])
        elif action == 'schedule':
            file_utils.save_schedule(request['tasks'])

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
