from logging import Logger

from slack_sdk.errors import SlackApiError
from sqlalchemy.exc import SQLAlchemyError
from weaviate.exceptions import WeaviateBaseError

import chatiq
from chatiq.repositories import SlackTeamRepository
from chatiq.vectorstore import Vectorstore

from .base import BaseHandler


class AppUninstalledHandler(BaseHandler):
    """Event handler for the "app_uninstalled" Slack event.

    This handler is invoked when the Slack application is uninstalled from a workspace.
    When the event occurs, it removes the corresponding Weaviate class associated with the workspace.

    Attributes:
        chatiq: An instance of the ChatIQ class.
    """

    def __init__(self, chatiq: "chatiq.ChatIQ") -> None:
        """Initializes the AppUninstalled with a ChatIQ instance.

        Args:
            chatiq (chatiq.ChatIQ): An instance of the ChatIQ class.
        """

        super().__init__(chatiq)

    def __call__(self, body: dict, logger: Logger) -> None:
        """Handle an "app_uninstalled" event.

        Args:
            body (dict): The body of the Slack event.
            logger (Logger): The logger to log debug and info messages.
        """

        try:
            logger.debug(f"App uninstalled on team: {body['team_id']}")

            with self.chatiq.db.transaction() as session:
                repo = SlackTeamRepository(session)
                repo.delete(body["team_id"])

            vectorstore = Vectorstore(self.chatiq.weaviate_client, body["team_id"])
            vectorstore.delete_index()

            logger.info(f"Deleted index from vectorstore on team: {body['team_id']}")
        except SlackApiError as e:
            logger.error(f"SlackApiError: {e}")
        except WeaviateBaseError as e:
            logger.error(f"WeaviateBaseError: {e}")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
