from flask import Flask

from svc.config.settings_state import Settings
from svc.controllers.hvac_queue_controller import update_hvac_worker
from svc.endpoints.app_routes import APP_BLUEPRINT
from svc.utilities.hvac_watcher import start_hvac_watcher
from svc.utilities.rabbitmq_client import RabbitMQClient


def create_app():
    app = Flask(__name__)

    app.register_blueprint(APP_BLUEPRINT)

    return app


def start_services(app):
    start_hvac_watcher()

    client = RabbitMQClient(Settings.get_instance())
    client.start_consumer(update_hvac_worker)
