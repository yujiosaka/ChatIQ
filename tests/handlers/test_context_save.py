from logging import Logger

import pytest
from slack_sdk import WebClient

from chatiq import ChatIQ
from chatiq.database import Database
from chatiq.handlers.context_save import ContextSaveHandler
from chatiq.models import SlackTeam
from chatiq.repositories import SlackTeamRepository


@pytest.fixture
def mock_team(mocker):
    mock_team = mocker.MagicMock(spec=SlackTeam)
    mock_team.model = "gpt-3.5-turbo"
    mock_team.temperature = 0.2
    mock_team.context = "Test context"
    return mock_team


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
def mock_ack(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_repository(mocker, mock_team):
    mock_repository = mocker.MagicMock(spec=SlackTeamRepository)
    mock_repository.update.return_value = mock_team
    mocker.patch("chatiq.handlers.context_save.SlackTeamRepository", return_value=mock_repository)
    return mock_repository


def test_context_save_handler_call(mock_chatiq, mock_client, mock_logger, mock_ack, mock_repository):
    context_save_handler = ContextSaveHandler(mock_chatiq)

    body = {
        "user": {"id": "U0JD6RS3T"},
        "team": {"id": "T0JD6RZU6"},
        "view": {"state": {"values": {"context_block": {"context_input": {"value": "Test context"}}}}},
    }
    context_save_handler(mock_client, body, mock_logger, mock_ack)

    mock_repository.update.assert_called_once_with(
        body["team"]["id"],
        {"context": body["view"]["state"]["values"]["context_block"]["context_input"]["value"]},
    )
    mock_ack.assert_called_once()
