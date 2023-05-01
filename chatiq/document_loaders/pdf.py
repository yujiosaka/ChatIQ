import logging
import tempfile
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Iterator, List

import requests
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.blob_loaders import Blob
from langchain.document_loaders.parsers.pdf import PyMuPDFParser
from langchain.text_splitter import TokenTextSplitter
from slack_bolt import BoltContext

from chatiq.constants import FILE_DOCUMENT_THREAD_TS
from chatiq.text_processor import TextProcessor
from chatiq.utils import pretty_json_dumps


class PdfLoader(BaseLoader):
    """A class for loading PDF files in Slack into Document objects.

    The PdfLoader class is a specialized document loader that takes a Slack message and PDF file
    and loads it into a Document object.
    """

    PDF_FILETYPE = "pdf"

    @classmethod
    def check_supported(cls, file: dict) -> bool:
        """Checks if the file is PDF

        Returns:
            bool: If the file is PDF or not
        """

        return file.get("filetype") == cls.PDF_FILETYPE

    def __init__(self, context: BoltContext, body: dict, file: dict, channel_type: str, model: str):
        """Initializes the PdfLoader with context and a Slack body.

        Args:
            context (BoltContext): Event context with bot tokens for API calls.
            body (dict): The Slack body to be loaded, represented as a dictionary.
            file (dict): The file attached to the message.
            channel_type (str): Type of the channel (channel, group, im or mpim)
            model (str): The name of the model used for tokenization.
        """

        token_length = TextProcessor.get_token_length_for_model(model)

        self.splitter = TokenTextSplitter(model_name=model, chunk_size=token_length)
        self.logger = logging.getLogger(__name__)
        self.context = context
        self.body = body
        self.file = file
        self.channel_type = channel_type
        self.parser = PyMuPDFParser()

    def __del__(self) -> None:
        """Deletes the instance of PdfLoader.

        Before the instance is deleted, it ensures any temporary files used during its lifecycle are closed properly.
        """
        if hasattr(self, "temp_file"):
            self.temp_file.close()

    def load(self) -> List[Document]:
        """Loads the PDF file into Document objects.

        Returns:
            List[Document]: A list containing Document objects.
        """

        if not self.check_supported(self.file):
            return []

        self._download_file()

        metadata = self._build_metadata()
        documents = list(self.lazy_load())
        content = "".join(doc.page_content for doc in documents)

        texts = self.splitter.split_text(content)
        page_count = len(texts)

        documents = []
        for i, text in enumerate(texts):
            page_content = pretty_json_dumps(
                {
                    "content_type": self.file["filetype"],
                    "user": self.body["event"]["user_id"],
                    "name": self.file["name"],
                    "title": self.file["title"],
                    "channel": self.body["event"]["channel_id"],
                    "content": text,
                    "page": f"{i + 1} / {page_count}",
                    "permalink": self.file["permalink"],
                    "timestamp": metadata["timestamp"],
                }
            )
            documents.append(Document(page_content=page_content, metadata=metadata))
        return documents

    def lazy_load(self) -> Iterator[Document]:
        """Lazily loads the content of the PDF file.

        Yields:
            Iterator[Document]: An iterator that yields Document objects.
        """

        blob = Blob.from_path(self.temp_file.name)
        yield from self.parser.parse(blob)

    def _download_file(self) -> None:
        """Downloads the file from Slack.

        The function uses the Slack API to download the file using the bot token and the URL
        stored in the file dictionary.

        Raises:
            ValueError: If there was an error in downloading the file.
        """

        self.logger.debug(f"Downloading file on team: {self.body['team_id']}")

        headers = {"Authorization": f"Bearer {self.context['bot_token']}"}
        response = requests.get(self.file["url_private"], headers=headers)
        if response.status_code != HTTPStatus.OK:
            error_message = f"Failed to download file. status code: {response.status_code}"
            self.logger.error(error_message)
            raise ValueError(error_message)

        self.temp_file = tempfile.NamedTemporaryFile()
        self.temp_file.write(response.content)

        self.logger.info(f"Downloaded file on team: {self.body['team_id']}")

    def _build_metadata(self) -> dict:
        """Builds metadata for the Document object based on the file dictionary.

        Returns:
            dict: A dictionary containing metadata information for a Document.

        Raises:
            ValueError: If the file's timestamp cannot be properly converted to a datetime object.
        """

        event_time = self.body["event_time"]

        try:
            timestamp = datetime.fromtimestamp(event_time, timezone.utc)
        except ValueError:
            error_message = f"Error converting date: {event_time}"
            self.logger.error(error_message)
            raise ValueError(error_message)

        return {
            "file_or_attachment_id": self.file["id"],
            "content_type": self.file["filetype"],
            "channel_type": self.channel_type,
            "channel_id": self.body["event"]["channel_id"],
            "thread_ts": FILE_DOCUMENT_THREAD_TS,
            "ts": self.body["event"]["event_ts"],
            "timestamp": timestamp.isoformat(),
            "permalink": self.file["permalink"],
        }
