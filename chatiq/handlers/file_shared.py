import threading
from logging import Logger
from typing import Optional, Tuple

from bs4 import BeautifulSoup
from slack_bolt import BoltContext
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sqlalchemy.exc import SQLAlchemyError
from weaviate.exceptions import WeaviateBaseError

import chatiq
from chatiq.document_loaders import PdfLoader, PlainTextLoader
from chatiq.repositories import SlackTeamRepository
from chatiq.vectorstore import Vectorstore

from .base import BaseHandler


class FileSharedHandler(BaseHandler):
    """Event handler for the "file_shared" Slack event.

    This handler is invoked when the file is shared from a message.
    When the event occurs, it adds the corresponding Weaviate objects associated with the file.

    Attributes:
        chatiq: An instance of the ChatIQ class.
    """

    def __init__(self, chatiq: "chatiq.ChatIQ") -> None:
        """Initializes the FileSharedHandler with a ChatIQ instance.

        Args:
            chatiq (chatiq.ChatIQ): An instance of the ChatIQ class.
        """

        super().__init__(chatiq)

    def __call__(self, client: WebClient, context: BoltContext, body: dict, logger: Logger) -> None:
        """Handle an "file_shared" event.

        Args:
            client (WebClient): The Slack WebClient for making API calls.
            context (BoltContext): Event context with bot tokens for API calls.
            body (dict): The body of the Slack message event.
            logger (Logger): The logger to log debug and info messages.
        """

        thread = threading.Thread(target=self._handle, args=(client, context, body, logger))
        self.chatiq.add_thread(thread)
        thread.start()

    def _handle(self, client: WebClient, context: BoltContext, body: dict, logger: Logger) -> None:
        """Actual handler function that processes the "file_shared" event. This function is run in a separate thread.

        Args:
            client (WebClient): The Slack WebClient for making API calls.
            context (BoltContext): Event context with bot tokens for API calls.
            body (dict): The body of the Slack message event.
            logger (Logger): The logger to log debug and info messages.
        """

        try:
            logger.debug(f"file shared on team: {body['team_id']}")

            file, content = self._get_file_info(client, body["event"]["file_id"])
            channel_type = self._get_channel_type(client, body["event"]["channel_id"])

            with self.chatiq.db.transaction() as session:
                repo = SlackTeamRepository(session)
                team = repo.get_or_create(body["team_id"], body["authorizations"][0]["user_id"])
                model = team.model

            vectorstore = Vectorstore(self.chatiq.weaviate_client, body["team_id"])
            vectorstore.ensure_index()

            documents = []
            if PdfLoader.check_supported(file):
                pdf_loader = PdfLoader(context, body, file, channel_type, model)  # type: ignore
                documents.extend(pdf_loader.load())

            if PlainTextLoader.check_supported(file):
                unfurling_link_loader = PlainTextLoader(content, body, file, channel_type, model)  # type: ignore
                documents.extend(unfurling_link_loader.load())

            for document in documents:
                # Iterating through the documents list and adding each document individually
                # to the vectorstore. While vectorstore.add_documents is capable of handling a list
                # of documents, a large batch of documents can cause a timeout error due to the
                # prolonged operation time. To prevent this, we add the documents one by one.
                vectorstore.add_documents([document])

            logger.info(f"Adding file from vectorstore on team: {body['team_id']}")
        except SlackApiError as e:
            logger.error(f"SlackApiError: {e}")
        except WeaviateBaseError as e:
            logger.error(f"WeaviateBaseError: {e}")
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")

    def _get_file_info(self, client: WebClient, file_id: str) -> Tuple[dict, Optional[str]]:
        """Retrieves the content of the file.

        Args:
            client (WebClient): The Slack WebClient for making API calls.
            file_id (str): The ID of file.

        Returns:
            Tuple[dict, Optional[str]]: The information and content of the file.
        """

        response = client.files_info(file=file_id)

        content = None
        if response.get("content"):
            content = response["content"]
        elif response.get("content_html"):
            soup = BeautifulSoup(response["content_html"], features="html.parser")
            content = soup.get_text()
        return response["file"], content

    def _get_channel_type(self, client: WebClient, channel_id: str) -> str:
        """Retrieves the content of the file.

        Args:
            client (WebClient): The Slack WebClient for making API calls.
            channel_id (str): The ID of channel.

        Returns:
            str: Type of the channel (channel, group, im or mpim)
        """

        response = client.conversations_info(channel=channel_id)

        if response["channel"]["is_channel"]:
            return "channel"
        elif response["channel"]["is_group"]:
            return "group"
        elif response["channel"]["is_im"]:
            return "im"
        elif response["channel"]["is_mpim"]:
            return "mpim"
        else:
            return "unknown"
