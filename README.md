# Project Purpose #
- Create linux service for automation thermostat
- Learn more about application hosting on Raspberry Pi

# Deployment #
1. Copy startService.sh to `/home/pi/` directory
    * execute `chmod +x startService.sh` to make it executable
2. Execute `startService.sh` file to create service
    * stops service if it is running
    * clones repo down if doesnt initially exist
    * does a pip install of all production dependencies
    * creates environment variable file `/home/pi/home_thermostat_/serviceEnvVariables`
    * copies `homeThermostat.service` file into systemd
    * registers and configures service
    * reboots the device
    * application will run on boot and pull in environment variables file


# Development #
1. After cloning repo:
    * create virtual environment: `virtualenv venv`
    * activate virtual environment: `source ./venv/scripts/activate`
    * install production dependencies: `pip install -Ur requirements.txt`
    * install test dependencies: `pip install -Ur test_requirements.txt`
2. Create `settings.json` file to substitute test environment variables
3. Provide any corresponding test coverage in directories `/test/integration` and `/test/unit`
4. Prior to committing code execute `./run_all_tests.sh`
5. Stand up application by executing `python app.py`
