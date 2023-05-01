from chatiq.block_builders import HomeScreenBlockBuilder
from chatiq.models import SlackTeam


def test_home_screen_block_builder():
    builder = HomeScreenBlockBuilder()

    assert builder.build() == []

    builder.add_spacer()
    assert builder.build() == [HomeScreenBlockBuilder.SPACER]

    builder.add_divider()
    assert builder.build() == [HomeScreenBlockBuilder.SPACER, HomeScreenBlockBuilder.DIVIDER]

    builder.add_header()
    assert builder.build() == [HomeScreenBlockBuilder.SPACER, HomeScreenBlockBuilder.DIVIDER, HomeScreenBlockBuilder.HEADER]

    builder.add_context_description_section()
    assert builder.build() == [
        HomeScreenBlockBuilder.SPACER,
        HomeScreenBlockBuilder.DIVIDER,
        HomeScreenBlockBuilder.HEADER,
        HomeScreenBlockBuilder.CONTEXT_DESCRIPTION_SECTION,
    ]

    builder.add_button_action()
    assert builder.build() == [
        HomeScreenBlockBuilder.SPACER,
        HomeScreenBlockBuilder.DIVIDER,
        HomeScreenBlockBuilder.HEADER,
        HomeScreenBlockBuilder.CONTEXT_DESCRIPTION_SECTION,
        HomeScreenBlockBuilder.BUTTON_ACTION,
    ]

    builder.add_tips_section()
    assert builder.build() == [
        HomeScreenBlockBuilder.SPACER,
        HomeScreenBlockBuilder.DIVIDER,
        HomeScreenBlockBuilder.HEADER,
        HomeScreenBlockBuilder.CONTEXT_DESCRIPTION_SECTION,
        HomeScreenBlockBuilder.BUTTON_ACTION,
        HomeScreenBlockBuilder.TIPS_SECTION,
    ]

    bot_id = "bot_id"
    builder.add_description_section(bot_id)
    assert builder.build()[-1]["text"]["text"] == f"To start a conversation, simply mention <@{bot_id}> in your message."

    model = "gpt-3.5-turbo"
    builder.add_model_section(model)
    assert builder.build()[-1]["accessory"]["initial_option"]["value"] == model

    temperature = "0.2"
    builder.add_temperature_section(temperature)
    assert builder.build()[-1]["accessory"]["initial_option"]["value"] == temperature

    context = "This is a context message"
    builder.add_context_section(context)
    assert builder.build()[-1]["element"]["initial_value"] == context


def test_build_home_screen():
    team = SlackTeam()
    team.bot_id = "bot_id"
    team.model = "gpt-3.5-turbo"
    team.temperature = 0.2
    team.context = "This is a context message"
    team.timezone_offset = "+09:00"

    blocks = HomeScreenBlockBuilder.build_home_screen(team)

    assert blocks[0] == HomeScreenBlockBuilder.HEADER
    assert blocks[1]["text"]["text"] == f"To start a conversation, simply mention <@{team.bot_id}> in your message."
    assert blocks[5]["accessory"]["initial_option"]["value"] == team.model
    assert blocks[9]["accessory"]["initial_option"]["value"] == str(team.temperature)
    assert blocks[13]["accessory"]["initial_option"]["value"] == str(team.timezone_offset)
    assert blocks[17]["element"]["initial_value"] == team.context
