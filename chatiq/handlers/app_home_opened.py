from logging import Logger

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sqlalchemy.exc import SQLAlchemyError

import chatiq
from chatiq.block_builders import HomeScreenBlockBuilder
from chatiq.repositories.slack_team_repository import SlackTeamRepository

from .base import BaseHandler


class AppHomeOpenedHandler(BaseHandler):
    """Event handler for the "app_home_opened" Slack event.

    Attributes:
        chatiq: An instance of the ChatIQ class.
    """

    def __init__(self, chatiq: "chatiq.ChatIQ") -> None:
        """Initializes the AppHomeOpenedHandler with a ChatIQ instance.

        Args:
            chatiq (chatiq.ChatIQ): An instance of the ChatIQ class.
        """

        self.chatiq = chatiq

    def __call__(self, client: WebClient, body: dict, logger: Logger) -> None:
        """Handle an "app_home_opened" event.

        This function builds the blocks for the App Home view and publishes it.

        Args:
            client (WebClient): The Slack WebClient to use for API calls.
            body (dict): The body of the event.
            logger (Logger): The logger to use for logging.
        """

        try:
            logger.debug(f"App Home opened on team: {body['team_id']}")

            with self.chatiq.db.transaction() as session:
                repo = SlackTeamRepository(session)
                team = repo.get_or_create(body["team_id"], body["authorizations"][0]["user_id"])
                blocks = HomeScreenBlockBuilder.build_home_screen(team)

            client.views_publish(user_id=body["event"]["user"], view={"type": "home", "blocks": blocks})

            logger.info(f"Published App Home on team: {body['team_id']}")
        except SlackApiError as e:
            logger.error(f"SlackApiError: {e}")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
