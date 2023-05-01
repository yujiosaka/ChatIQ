from chatiq.block_builders import ChannelConfigurationBlockBuilder
from chatiq.models import SlackTeam


def test_home_screen_block_builder():
    builder = ChannelConfigurationBlockBuilder()

    assert builder.build() == []

    builder.add_header()
    assert builder.build()[-1]["text"]["text"] == "Configuration is set for this channel"

    builder.add_temperature_and_timezone_offset_section(1.0, None)
    assert builder.build()[-1]["fields"] == [{"type": "mrkdwn", "text": "*AI temperature:*\n1.0"}]

    builder.add_temperature_and_timezone_offset_section(None, "+09:00")
    assert builder.build()[-1]["fields"] == [{"type": "mrkdwn", "text": "*Timezone:*\n+09:00"}]

    builder.add_context_section("Speak like a pirate")
    assert builder.build()[-1]["text"]["text"] == "*System Message*\nSpeak like a pirate"


def test_build_home_screen():
    empty_blocks = ChannelConfigurationBlockBuilder.build_channel_configuration(None, None, None)
    assert len(empty_blocks) == 0

    timezone_offset_only_blocks = ChannelConfigurationBlockBuilder.build_channel_configuration(None, "+09:00", None)
    assert len(timezone_offset_only_blocks) == 2
    assert timezone_offset_only_blocks[0]["text"]["text"] == "Configuration is set for this channel"
    assert timezone_offset_only_blocks[1]["fields"] == [{"type": "mrkdwn", "text": "*Timezone:*\n+09:00"}]

    context_only_blocks = ChannelConfigurationBlockBuilder.build_channel_configuration(None, None, "Speak like a pirate")
    assert len(context_only_blocks) == 2
    assert context_only_blocks[0]["text"]["text"] == "Configuration is set for this channel"
    assert context_only_blocks[1]["text"]["text"] == "*System Message*\nSpeak like a pirate"

    full_blocks = ChannelConfigurationBlockBuilder.build_channel_configuration("1.0", "+09:00", "Speak like a pirate")
    assert len(full_blocks) == 3
    assert full_blocks[0]["text"]["text"] == "Configuration is set for this channel"
    assert full_blocks[1]["fields"] == [
        {"type": "mrkdwn", "text": "*AI temperature:*\n1.0"},
        {"type": "mrkdwn", "text": "*Timezone:*\n+09:00"},
    ]
    assert full_blocks[2]["text"]["text"] == "*System Message*\nSpeak like a pirate"
