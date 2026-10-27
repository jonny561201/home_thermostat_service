class Mime:
    JSON = 'application/json'


class Mode:
    BLOWER = 'blower'
    COOLING = 'cooling'
    HEATING = 'heating'
    TURN_OFF = 'off'
    AUTO = 'auto'


class Hvac:
    MODE = Mode
    QUEUE = 'home-automation-hvac'
    FURNACE = 'furnace'
    AIR_CONDITIONING = 'ac'
    AUTO_BAND = 1.0
    DEADBAND = 0.5
    MIN_ON_SECONDS = 300
    MIN_OFF_SECONDS = 300
    DEFAULT_DESIRED_TEMP = 21.1111
    WATCH_INTERVAL_SECONDS = 60
    RECONNECT_SECONDS = 5


class Time:
    FIVE_SECONDS = 5
    SEVEN_SECONDS = 7
    TEN_SECONDS = 10
    TWENTY_SECONDS = 20
    THIRTY_SECONDS = 30
    ONE_MINUTE = 60
    TWO_MINUTE = 120
    FIVE_MINUTE = 300
    TEN_MINUTE = 600


class Automation:
    APP_NAME = "Soaring Leaf Home Automation"
    HVAC = Hvac
    TIME = Time
