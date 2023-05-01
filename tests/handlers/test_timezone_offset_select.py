from logging import Logger

import pytest
from slack_sdk import WebClient

from chatiq import ChatIQ
from chatiq.database import Database
from chatiq.handlers import TimezoneOffsetSelectHandler
from chatiq.models import SlackTeam
from chatiq.repositories import SlackTeamRepository


@pytest.fixture
def mock_team(mocker):
    mock_team = mocker.MagicMock(spec=SlackTeam)
    mock_team.timezone_offset = "+00:00"
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
    mocker.patch("chatiq.handlers.timezone_offset_select.SlackTeamRepository", return_value=mock_repository)
    return mock_repository


def test_timezone_select_handler_call(mock_chatiq, mock_client, mock_logger, mock_ack, mock_repository):
    timezone_offset_select_handler = TimezoneOffsetSelectHandler(mock_chatiq)

    body = {
        "user": {"id": "U0JD6RS3T"},
        "team": {"id": "T0JD6RZU6"},
        "view": {
            "state": {
                "values": {"timezone_offset_block": {"timezone_offset_select": {"selected_option": {"value": "+09:00"}}}}
            }
        },
    }
    timezone_offset_select_handler(mock_client, body, mock_logger, mock_ack)
    mock_repository.update.assert_called_once_with(
        body["team"]["id"],
        {
            "timezone_offset": body["view"]["state"]["values"]["timezone_offset_block"]["timezone_offset_select"][
                "selected_option"
            ]["value"]
        },
    )
    mock_ack.assert_called_once()
