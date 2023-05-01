from logging import Logger

import pytest
from slack_sdk import WebClient

from chatiq import ChatIQ
from chatiq.database import Database
from chatiq.handlers import AppHomeOpenedHandler
from chatiq.models import SlackTeam
from chatiq.repositories.slack_team_repository import SlackTeamRepository


@pytest.fixture
def mock_chatiq(mocker):
    mock_chatiq = mocker.MagicMock(spec=ChatIQ)
    mock_chatiq.db = mocker.MagicMock(spec=Database)
    return mock_chatiq


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock(spec=WebClient)


@pytest.fixture
def mock_logger(mocker):
    return mocker.MagicMock(spec=Logger)


@pytest.fixture
def mock_team(mocker):
    mock_team = mocker.MagicMock(spec=SlackTeam)
    mock_team.model = "gpt-3.5-turbo"
    mock_team.temperature = 0.2
    mock_team.context = "Test context"
    return mock_team


@pytest.fixture
def mock_repository(mocker, mock_team):
    mock_repository = mocker.MagicMock(spec=SlackTeamRepository)
    mock_repository.return_value = mock_team
    mocker.patch("chatiq.handlers.app_home_opened.SlackTeamRepository", return_value=mock_repository)
    return mock_repository


def test_app_home_opened_handler_call(mock_chatiq, mock_client, mock_logger, mock_repository):
    app_home_opened_handler = AppHomeOpenedHandler(mock_chatiq)

    body = {"team_id": "T0JD6RZU6", "authorizations": [{"user_id": "U0JD6RZU6"}], "event": {"user": "U0JD6RZU6"}}
    app_home_opened_handler(mock_client, body, mock_logger)

    mock_repository.get_or_create.assert_called_once_with(body["team_id"], body["authorizations"][0]["user_id"])
    mock_client.views_publish.assert_called_once()
