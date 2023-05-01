from typing import Optional, Tuple

from chatiq.exceptions import TemperatureRangeError, TimezoneOffsetSelectError
from chatiq.models import SlackTeam
from chatiq.utils import extract_emoji_text


class ChannelInfoParser:
    """
    A class for parsing information from the topic and description of a Slack channel.

    Args:
        topic (str): The topic of the Slack channel.
        description (str): The description of the Slack channel.
    """

    TEMPERATURE_EMOJI: str = ":thermometer:"
    TIMEZONE_OFFSET_EMOJI: str = ":round_pushpin:"
    CONTEXT_EMOJI: str = ":speech_balloon:"

    def __init__(self, topic: str, description: str) -> None:
        """Initialize a new instance of the ChannelInfoParser class.

        Args:
            topic: The topic of the Slack channel.
            description: The description of the Slack channel.
        """

        self.topic = topic
        self.description = description

    def parse(self) -> Tuple[Optional[float], Optional[str], Optional[str]]:
        """Parse information from the topic and description of a Slack channel.

        Returns:
            Tuple[Optional[float], Optional[str], Optional[str]]: A tuple containing the parsed temperature,
            timezone offset, and context.

        Raises:
            TemperatureRangeError: If the temperature value is invalid or out of range.
            TimezoneOffsetSelectError: If the timezone offset is invalid.
        """

        temperature = self._parse_temperature()
        timezone_offset = self._parse_timezone_offset()
        context = self._parse_context()
        return temperature, timezone_offset, context

    def _parse_temperature(self) -> Optional[float]:
        """Parse the temperature for the AI model from the topic and description of the Slack channel.

        Returns:
            Optional[float]: The temperature for the AI model.

        Raises:
            TemperatureRangeError: If the temperature value is invalid or out of range.
        """

        temperature_str = extract_emoji_text(self.topic, self.TEMPERATURE_EMOJI) or extract_emoji_text(
            self.description, self.TEMPERATURE_EMOJI
        )

        if temperature_str:
            try:
                temperature = float(temperature_str)
            except ValueError:
                raise TemperatureRangeError(f"Invalid temperature value: {temperature_str}")

            if not (SlackTeam.MIN_TEMPERATURE <= temperature <= SlackTeam.MAX_TEMPERATURE):
                raise TemperatureRangeError(f"Temperature value out of range: {temperature}")

            return temperature

        return None

    def _parse_timezone_offset(self) -> Optional[str]:
        """Parse the timezone offset from the topic and description of the Slack channel.

        Returns:
            Optional[str]: The timezone offset.

        Raises:
            TimezoneOffsetSelectError: If the timezone offset is invalid.
        """

        timezone_offset = extract_emoji_text(self.topic, self.TIMEZONE_OFFSET_EMOJI) or extract_emoji_text(
            self.description, self.TIMEZONE_OFFSET_EMOJI
        )

        if timezone_offset and timezone_offset not in SlackTeam.TIMEZONE_OFFSETS:
            raise TimezoneOffsetSelectError(f"Invalid timezone offset: {timezone_offset}.")

        return timezone_offset

    def _parse_context(self) -> Optional[str]:
        """Parse the context for the AI model from the topic and description of the Slack channel.

        Returns:
            Optional[str]: The context for the AI model.
        """

        return extract_emoji_text(self.topic, self.CONTEXT_EMOJI) or extract_emoji_text(self.description, self.CONTEXT_EMOJI)
