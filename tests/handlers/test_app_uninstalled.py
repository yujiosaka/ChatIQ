from logging import Logger

import pytest
from weaviate import Client

from chatiq import ChatIQ
from chatiq.database import Database
from chatiq.handlers import AppUninstalledHandler
from chatiq.repositories import SlackTeamRepository
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
def mock_repository(mocker):
    mock_repository = mocker.MagicMock(spec=SlackTeamRepository)
    mocker.patch("chatiq.handlers.app_uninstalled.SlackTeamRepository", return_value=mock_repository)
    return mock_repository


@pytest.fixture
def mock_vectorstore(mocker):
    mock_vectorstore = mocker.MagicMock(spec=Vectorstore)
    mocker.patch("chatiq.handlers.app_uninstalled.Vectorstore", return_value=mock_vectorstore)
    return mock_vectorstore


def test_app_uninstalled_handler_call(mock_chatiq, mock_logger, mock_repository, mock_vectorstore):
    app_uninstalled_handler = AppUninstalledHandler(mock_chatiq)

    body = {"team_id": "T0JD6RZU6"}
    app_uninstalled_handler(body, mock_logger)

    mock_repository.delete.assert_called_once_with(body["team_id"])
    mock_vectorstore.delete_index.assert_called_once()
