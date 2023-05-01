from typing import List


class ChannelConfigurationBlockBuilder:
    """A builder for creating Slack block elements of channel configuration.

    This class encapsulates the creation of different block elements used in channel configuration.
    It follows the builder pattern, allowing a fluent interface for creating blocks.
    """

    HEADER = {"type": "section", "text": {"type": "plain_text", "text": "Configuration is set for this channel"}}

    @classmethod
    def build_channel_configuration(cls, temperature: float, timezone_offset: str, context: str) -> List[dict]:
        """Builds the blocks for the channel configuration view.

        Args:
            temperature (float): The temperature of the team configuration.
            context (str): The context of the team configuration.
            timezone_offset (str): The timezone_offset of the team configuration.

        Returns:
            List[dict]: A list of blocks for the App Home view.
        """

        builder = ChannelConfigurationBlockBuilder()

        if temperature or timezone_offset or context:
            builder = builder.add_header()

        if temperature or timezone_offset:
            builder = builder.add_temperature_and_timezone_offset_section(temperature, timezone_offset)

        if context:
            builder = builder.add_context_section(context)

        return builder.build()

    def __init__(self):
        """Initializes a new ChannelConfigurationBlockBuilder instance."""

        self.blocks = []

    def build(self) -> List[dict]:
        """Finalizes the building process and returns the created blocks.

        Returns:
            list: A list of block elements.
        """

        return self.blocks

    def add_header(self) -> "ChannelConfigurationBlockBuilder":
        """Adds a header block to the blocks.

        Returns:
            ChannelConfigurationBlockBuilder: The instance of the ChannelConfigurationBlockBuilder for chaining.
        """

        self.blocks.append(self.HEADER)
        return self

    def add_temperature_and_timezone_offset_section(
        self, temperature: float, timezone_offset: str
    ) -> "ChannelConfigurationBlockBuilder":
        """Adds a temperature and timezone offset section block to the blocks.

        Args:
            temperature (float): The temperature of the team configuration.
            timezone_offset (str): The timezone_offset of the team configuration.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        fields = []
        if temperature:
            fields.append({"type": "mrkdwn", "text": f"*AI temperature:*\n{temperature}"})
        if timezone_offset:
            fields.append({"type": "mrkdwn", "text": f"*Timezone:*\n{timezone_offset}"})

        self.blocks.append({"type": "section", "fields": fields})
        return self

    def add_context_section(self, context: str) -> "ChannelConfigurationBlockBuilder":
        """Adds a context section block to the blocks.

        Args:
            context (str): The context of the team configuration.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*System Message*\n{context}"}})
        return self
