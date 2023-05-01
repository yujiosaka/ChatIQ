from logging import Logger

from slack_sdk.errors import SlackApiError
from weaviate.exceptions import WeaviateBaseError

import chatiq
from chatiq.vectorstore import Vectorstore

from .base import BaseHandler


class FileDeletedHandler(BaseHandler):
    """Event handler for the "file_deleted" Slack event.

    This handler is invoked when the file is deleted from a message.
    When the event occurs, it removes the corresponding Weaviate objects associated with the file.

    Attributes:
        chatiq: An instance of the ChatIQ class.
    """

    def __init__(self, chatiq: "chatiq.ChatIQ") -> None:
        """Initializes the FileDeletedHandler with a ChatIQ instance.

        Args:
            chatiq (chatiq.ChatIQ): An instance of the ChatIQ class.
        """

        super().__init__(chatiq)

    def __call__(self, body: dict, logger: Logger) -> None:
        """Handle an "file_deleted" event.

        Args:
            body (dict): The body of the Slack event.
            logger (Logger): The logger to log debug and info messages.

        Raises:
            WeaviateBaseError: If there is any error while deleting the index.
        """

        try:
            logger.debug(f"file deleteed on team: {body['team_id']}")

            vectorstore = Vectorstore(self.chatiq.weaviate_client, body["team_id"])
            vectorstore.ensure_index()
            vectorstore.delete_file_or_attachment(body["event"]["file_id"])

            logger.info(f"Deleted file from vectorstore on team: {body['team_id']}")
        except SlackApiError as e:
            logger.error(f"SlackApiError: {e}")
        except WeaviateBaseError as e:
            logger.error(f"WeaviateBaseError: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
