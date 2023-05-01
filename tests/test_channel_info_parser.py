import pytest

from chatiq.channel_info_parser import ChannelInfoParser
from chatiq.exceptions import TemperatureRangeError, TimezoneOffsetSelectError

FULL_EMOJI_TEXT = """
:thermometer: 2.0
:round_pushpin: +03:00
:speech_balloon: Assistant should speak like a viking
"""


def test_parse_empty_topic_and_description():
    parser = ChannelInfoParser("", "")
    temperature, timezone_offset, context = parser.parse()

    assert temperature is None
    assert timezone_offset is None
    assert context is None


def test_parse_no_emojis():
    parser = ChannelInfoParser("Today is Jimmy's birthday!", "Celebrate our birthdays!")
    temperature, timezone_offset, context = parser.parse()

    assert temperature is None
    assert timezone_offset is None
    assert context is None


def test_parse_emojis_in_topic_and_description():
    parser = ChannelInfoParser(FULL_EMOJI_TEXT, FULL_EMOJI_TEXT)
    temperature, timezone_offset, context = parser.parse()

    assert temperature == 2.0
    assert timezone_offset == "+03:00"
    assert context == "Assistant should speak like a viking"


@pytest.mark.parametrize("temperature_str", ["invalid", "10.5"])
def test_parse_invalid_temperature(temperature_str):
    parser = ChannelInfoParser(f":thermometer: {temperature_str}", "")
    with pytest.raises(TemperatureRangeError):
        parser.parse()


@pytest.mark.parametrize("timezone_offset", ["+9:00", "invalid"])
def test_parse_invalid_timezone_offset(timezone_offset):
    parser = ChannelInfoParser("", f":round_pushpin: {timezone_offset}")
    with pytest.raises(TimezoneOffsetSelectError):
        parser.parse()
