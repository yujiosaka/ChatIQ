from logging import Logger

import pytest
from weaviate import Client

from chatiq import ChatIQ
from chatiq.database import Database
from chatiq.handlers import FileDeletedHandler
from chatiq.vectorstore import Vectorstore


@pytest.fixture
def mock_chatiq(mocker):
    mock_chatiq = mocker.MagicMock(spec=ChatIQ)
    mock_chatiq.weaviate_client = mocker.MagicMock(spec=Client)
    mock_chatiq.db = mocker.MagicMock(spec=Database)
    return mock_chatiq


@pytest.fixture
def mock_logger(mocker):
    return mocker.MagicMock(spec=Logger)


@pytest.fixture
def mock_vectorstore(mocker):
    mock_vectorstore = mocker.MagicMock(spec=Vectorstore)
    mocker.patch("chatiq.handlers.file_deleted.Vectorstore", return_value=mock_vectorstore)
    return mock_vectorstore


def test_file_deleted_handler_call(mock_chatiq, mock_logger, mock_vectorstore):
    file_deleted_handler = FileDeletedHandler(mock_chatiq)

    body = {"team_id": "T0JD6RZU6", "event": {"file_id": "F0JD6RZU6"}}
    file_deleted_handler(body, mock_logger)

    mock_vectorstore.ensure_index.assert_called_once()
    mock_vectorstore.delete_file_or_attachment.assert_called_once_with("F0JD6RZU6")
