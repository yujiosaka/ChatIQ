from logging import Logger

import pytest
from weaviate import Client

from chatiq import ChatIQ
from chatiq.database import Database
from chatiq.handlers import ChannelDeletedHandler
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
    mocker.patch("chatiq.handlers.channel_deleted.Vectorstore", return_value=mock_vectorstore)
    return mock_vectorstore


def test_channel_deleted_handler_call(mock_chatiq, mock_logger, mock_vectorstore):
    channel_deleted_handler = ChannelDeletedHandler(mock_chatiq)

    body = {"team_id": "T0JD6RZU6", "event": {"channel": "C024BE91L"}}
    channel_deleted_handler(body, mock_logger)

    mock_vectorstore.ensure_index.assert_called_once()
    mock_vectorstore.delete_channel.assert_called_once_with("C024BE91L")
