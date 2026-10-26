import logging

from svc.manager import create_app, start_services


logging.basicConfig(filename='thermostat.log', level=logging.INFO)

app = create_app()
start_services(app)

if __name__ == '__main__':
    app.run()
