from typing import List

from chatiq.models import SlackTeam
from chatiq.utils import format_mention, get_emoji_from_timezone_offset


class HomeScreenBlockBuilder:
    """A builder for creating Slack block elements of Home Screen.

    This class encapsulates the creation of different block elements used in Home Screen.
    It follows the builder pattern, allowing a fluent interface for creating blocks.
    """

    MODEL_OPTIONS = [{"text": {"type": "plain_text", "text": ":rocket:  GPT 3.5"}, "value": "gpt-3.5-turbo"}]
    TEMPERATURE_OPTIONS = [
        {"text": {"type": "plain_text", "text": ":snowflake:  Focused (0)"}, "value": "0.0"},
        {"text": {"type": "plain_text", "text": ":cloud:  Moderate (0.2)"}, "value": "0.2"},
        {"text": {"type": "plain_text", "text": ":partly_sunny:  Balanced (0.4)"}, "value": "0.4"},
        {"text": {"type": "plain_text", "text": ":sunny:  Creative (1.0)"}, "value": "1.0"},
        {"text": {"type": "plain_text", "text": ":fire:  Random (2.0)"}, "value": "2.0"},
    ]
    TIMEZONE_OFFSET_OPTIONS = [
        {"text": {"type": "plain_text", "text": f"{get_emoji_from_timezone_offset(offset)}  {offset}"}, "value": offset}
        for offset in SlackTeam.TIMEZONE_OFFSETS
    ]
    HEADER = {"type": "header", "text": {"type": "plain_text", "text": ":wave:  Welcome to ChatIQ"}}
    SPACER = {"type": "section", "text": {"type": "mrkdwn", "text": " "}}
    DIVIDER = {"type": "divider"}
    CONTEXT_DESCRIPTION_SECTION = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "This message shapes how the AI interacts in your conversations.",
        },
    }
    TIPS_SECTION = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                ":bulb: *Tips*\n\n"
                "- You can customize settings for each channel in its description or topic.\n"
                "- Use :thermometer: for temperature, "
                ":round_pushpin: for timezone and :speech_balloon: for system message.\n"
                "- Remember, channel topic > channel description > home screen in priority."
            ),
        },
    }
    BUTTON_ACTION = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Save"},
                "value": "save",
                "style": "primary",
                "action_id": "context_save",
            }
        ],
    }

    @classmethod
    def build_home_screen(cls, team: "SlackTeam") -> List[dict]:
        """Builds the blocks for the App Home view.

        Args:
            team (SlackTeam): The SlackTeam instance to use for building the blocks.

        Returns:
            List[dict]: A list of blocks for the App Home view.
        """

        return (
            HomeScreenBlockBuilder()
            .add_header()
            .add_description_section(team.bot_id)  # type: ignore
            .add_spacer()
            .add_divider()
            .add_spacer()
            .add_model_section(team.model)  # type: ignore
            .add_spacer()
            .add_divider()
            .add_spacer()
            .add_temperature_section(str(team.temperature))  # type: ignore
            .add_spacer()
            .add_divider()
            .add_spacer()
            .add_timezone_offset_section(team.timezone_offset)  # type: ignore
            .add_spacer()
            .add_divider()
            .add_spacer()
            .add_context_section(team.context)  # type: ignore
            .add_context_description_section()
            .add_button_action()
            .add_spacer()
            .add_divider()
            .add_spacer()
            .add_tips_section()
            .build()
        )

    def __init__(self):
        """Initializes a new HomeScreenBlockBuilder instance."""

        self.blocks = []

    def build(self) -> List[dict]:
        """Finalizes the building process and returns the created blocks.

        Returns:
            list: A list of block elements.
        """

        return self.blocks

    def add_spacer(self) -> "HomeScreenBlockBuilder":
        """Adds a spacer block to the blocks.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(self.SPACER)
        return self

    def add_divider(self) -> "HomeScreenBlockBuilder":
        """Adds a divider block to the blocks.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(self.DIVIDER)
        return self

    def add_header(self) -> "HomeScreenBlockBuilder":
        """Adds a header block to the blocks.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(self.HEADER)
        return self

    def add_context_description_section(self) -> "HomeScreenBlockBuilder":
        """Adds a context description section block to the blocks.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(self.CONTEXT_DESCRIPTION_SECTION)
        return self

    def add_button_action(self) -> "HomeScreenBlockBuilder":
        """Adds a button action block to the blocks.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(self.BUTTON_ACTION)
        return self

    def add_tips_section(self) -> "HomeScreenBlockBuilder":
        """Adds a tips action block to the blocks.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(self.TIPS_SECTION)
        return self

    def add_description_section(self, bot_id: str) -> "HomeScreenBlockBuilder":
        """Builds the description section block for the App Home view.

        Args:
            bot_id (str): The ID of the bot.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"To start a conversation, simply mention {format_mention(bot_id)} in your message.",
                },
            }
        )
        return self

    def add_model_section(self, model: str) -> "HomeScreenBlockBuilder":
        """Builds the model selection block for the App Home view.

        Args:
            model (str): The model to pre-select.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        initial_option = next((option for option in self.MODEL_OPTIONS if option["value"] == model), None)
        self.blocks.append(
            {
                "block_id": "model_block",
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":zap:  *Choose your AI model*\n\nThis decides the intelligence level of your AI assistant.",
                },
                "accessory": {
                    "action_id": "model_select",
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select an AI model"},
                    "options": self.MODEL_OPTIONS,
                    "initial_option": initial_option,
                },
            }
        )
        return self

    def add_temperature_section(self, temperature: str) -> "HomeScreenBlockBuilder":
        """Builds the temperature selection block for the App Home view.

        Args:
            temperature (str): The temperature to pre-select.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        initial_option = next((option for option in self.TEMPERATURE_OPTIONS if option["value"] == temperature), None)
        self.blocks.append(
            {
                "block_id": "temperature_block",
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        ":thermometer:  *Set your preferred AI temperature*.\n\n"
                        "This adjusts the creativity of the AI assistant."
                    ),
                },
                "accessory": {
                    "action_id": "temperature_select",
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select a temperature"},
                    "options": self.TEMPERATURE_OPTIONS,
                    "initial_option": initial_option,
                },
            }
        )
        return self

    def add_timezone_offset_section(self, timezone_offset: str) -> "HomeScreenBlockBuilder":
        """Builds the timezone offset selection block for the App Home view.

        Args:
            timezone_offset (str): The timezone offset to pre-select.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        initial_option = next(
            (option for option in self.TIMEZONE_OFFSET_OPTIONS if option["value"] == timezone_offset), None
        )
        self.blocks.append(
            {
                "block_id": "timezone_offset_block",
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        ":round_pushpin:  *Set your preferred timezone*.\n\n"
                        "This helps the AI assistant understand your local time."
                    ),
                },
                "accessory": {
                    "action_id": "timezone_offset_select",
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select a timezone offset"},
                    "options": self.TIMEZONE_OFFSET_OPTIONS,
                    "initial_option": initial_option,
                },
            }
        )
        return self

    def add_context_section(self, context: str) -> "HomeScreenBlockBuilder":
        """Builds the context input block for the App Home view.

        Args:
            context (str): The initial value for the context input.

        Returns:
            HomeScreenBlockBuilder: The instance of the HomeScreenBlockBuilder for chaining.
        """

        self.blocks.append(
            {
                "block_id": "context_block",
                "type": "input",
                "element": {
                    "action_id": "context_input",
                    "type": "plain_text_input",
                    "multiline": True,
                    "max_length": 256,
                    "placeholder": {"type": "plain_text", "text": "Assistant is designed to be..."},
                    "initial_value": context,
                },
                "label": {"type": "plain_text", "text": ":speech_balloon:  Enter System Message"},
            }
        )
        return self
