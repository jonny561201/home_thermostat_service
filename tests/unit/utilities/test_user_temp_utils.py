from src.utilities.user_temp_utils import get_user_temperature


def test_get_user_temperature__should_return_temperature_in_celsius():
    temp_text = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES',
                 '72 01 4b 46 7f ff 0e 10 57 t=23125']
    actual = get_user_temperature(temp_text, False)

    assert actual == 23.12


def test_get_user_temperature__should_return_temperature_in_fahrenheit():
    temp_text = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES',
                 '72 01 4b 46 7f ff 0e 10 57 t=12451']
    actual = get_user_temperature(temp_text, True)

    assert actual == 54.41


def test_get_user_temperature__should_throw_conflict_when_error_reading_temp():
    temp_text = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 NOPE']
    actual = get_user_temperature(temp_text, False)

    assert actual == 0.0


def test_get_user_temperature__should_throw_conflict_when_no_temp_text_found():
    temp_text = ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES',
                 '72 01 4b 46 7f ff 0e 10 57']
    actual = get_user_temperature(temp_text, False)

    assert actual == 0.0


def test_get_user_temperature__should_return_zero_when_text_file_is_none():
    actual = get_user_temperature(None, False)

    assert actual == 0.0

