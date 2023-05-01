from logging import Logger
from typing import Callable

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sqlalchemy.exc import SQLAlchemyError

import chatiq
from chatiq.block_builders import HomeScreenBlockBuilder
from chatiq.exceptions import TemperatureRangeError
from chatiq.repositories import SlackTeamRepository

from .base import BaseHandler


class TemperatureSelectHandler(BaseHandler):
    """Event handler for temperature selection in the application.

    Attributes:
        chatiq (chatiq.ChatIQ): An instance of the ChatIQ class.
    """

    def __init__(self, chatiq: "chatiq.ChatIQ") -> None:
        """Initializes an instance of TemperatureSelectHandler.

        Args:
            chatiq (chatiq.ChatIQ): An instance of the ChatIQ class.
        """

        super().__init__(chatiq)

    def __call__(self, client: WebClient, body: dict, logger: Logger, ack: Callable[..., None]) -> None:
        """Handles temperature selection event by saving the selected temperature for a team.

        Args:
            client (WebClient): The Slack WebClient for making API calls.
            body (dict): The body of the Slack event.
            logger (Logger): The logger to log debug and info messages.
            ack (Callable[..., None]): Acknowledgement function to respond to the event.
        """

        select = body["view"]["state"]["values"]["temperature_block"]["temperature_select"]

        try:
            logger.debug(f"Saving temperature on team: {body['team']['id']}")

            with self.chatiq.db.transaction() as session:
                repo = SlackTeamRepository(session)
                team = repo.update(body["team"]["id"], {"temperature": float(select["selected_option"]["value"])})
                blocks = HomeScreenBlockBuilder.build_home_screen(team)

            client.views_publish(user_id=body["user"]["id"], view={"type": "home", "blocks": blocks})
            ack()

            logger.info(f"Saved temperature on team: {body['team']['id']}")
        except TemperatureRangeError as e:
            logger.error(f"TemperatureRangeError: {e}")
        except SlackApiError as e:
            logger.error(f"SlackApiError: {e}")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
