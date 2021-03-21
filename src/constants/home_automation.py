class Mode:
    BLOWER = 'blower'
    COOLING = 'cooling'
    HEATING = 'heating'
    TURN_OFF = 'off'


class Hvac:
    MODE = Mode
    FURNACE = 'furnace'
    AIR_CONDITIONING = 'ac'
    MIN_COOLING = 15.0
    MAX_HEATING = 25.0


class Garage:
    OPEN = True
    CLOSED = False


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


class Light:
    TURN_ON = 'turn on'
    TURN_OFF = 'turn off'
    SUNRISE = 'sunrise alarm'


class Automation:
    APP_NAME = "Soaring Leaf Home Automation"
    HVAC = Hvac
    TIME = Time
    GARAGE = Garage
    LIGHT = Light
