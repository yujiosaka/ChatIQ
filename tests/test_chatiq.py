import threading
from unittest.mock import call

import pytest
import slack_bolt
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
from weaviate import Client

from chatiq import ChatIQ
from chatiq.database import Database
from chatiq.exceptions import SettingsValidationError


@pytest.fixture
def mock_env_variables(monkeypatch):
    monkeypatch.delenv("SLACK_CLIENT_ID", raising=False)
    monkeypatch.delenv("SLACK_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("WEAVIATE_URL", raising=False)


@pytest.fixture
def mock_weaviate_client(mocker):
    mock_weaviate_client = mocker.MagicMock(spec=Client)
    mocker.patch("chatiq.chatiq.Client", return_value=mock_weaviate_client)
    return mock_weaviate_client


@pytest.fixture
def mock_database(mocker):
    mock_database = mocker.MagicMock(spec=Database)
    mock_database.installation_store = mocker.MagicMock(spec=SQLAlchemyInstallationStore)
    mock_database.state_store = mocker.MagicMock(spec=SQLAlchemyOAuthStateStore)
    mocker.patch("chatiq.chatiq.Database", return_value=mock_database)
    return mock_database


@pytest.fixture
def mock_bolt_app(mocker):
    bolt_app = mocker.patch.object(slack_bolt, "App", autospec=True)
    bolt_app.return_value = bolt_app
    return bolt_app


def test_missing_setting_without_bolt_app(mock_env_variables, mock_weaviate_client, mock_database):
    with pytest.raises(SettingsValidationError):
        ChatIQ()


def test_environment_variables_settings_without_bolt_app(
    mock_env_variables,
    mock_weaviate_client,
    mock_database,
    monkeypatch,
):
    monkeypatch.setenv("SLACK_CLIENT_ID", "slack-client-id")
    monkeypatch.setenv("SLACK_CLIENT_SECRET", "slack-client-secret")
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "slack-signing-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-api-key")
    monkeypatch.setenv("POSTGRES_URL", "postgres-url")
    monkeypatch.setenv("WEAVIATE_URL", "weaviate-url")

    ChatIQ()


def test_argument_settings_without_bolt_app(mock_env_variables, mock_weaviate_client, mock_database):
    ChatIQ(
        slack_client_id="test_client_id",
        slack_client_secret="test_client_secret",
        slack_signing_secret="test_signing_secret",
        openai_api_key="test_openai_api_key",
        postgres_url="test_postgres_url",
        weaviate_url="test_weaviate_url",
    )


def test_missing_setting_with_bolt_app(mock_env_variables, mock_weaviate_client, mock_database, mock_bolt_app):
    ChatIQ(
        bolt_app=mock_bolt_app,
        openai_api_key="test_openai_api_key",
        postgres_url="test_postgres_url",
        weaviate_url="test_weaviate_url",
    )


def test_environment_variables_settings_with_bolt_app(
    mock_env_variables, mock_weaviate_client, mock_database, mock_bolt_app, monkeypatch
):
    monkeypatch.setenv("OPENAI_API_KEY", "openai-api-key")
    monkeypatch.setenv("POSTGRES_URL", "postgres-url")
    monkeypatch.setenv("WEAVIATE_URL", "weaviate-url")

    ChatIQ(bolt_app=mock_bolt_app)


def test_argument_settings_with_bolt_app(mock_env_variables, mock_weaviate_client, mock_database, mock_bolt_app):
    with pytest.raises(SettingsValidationError):
        ChatIQ(bolt_app=mock_bolt_app)


def test_rate_limit_retry_handler(mock_env_variables, mock_weaviate_client, mock_database, mock_bolt_app):
    ChatIQ(
        bolt_app=mock_bolt_app,
        slack_client_id="test_client_id",
        slack_client_secret="test_client_secret",
        slack_signing_secret="test_signing_secret",
        openai_api_key="test_openai_api_key",
        postgres_url="test_postgres_url",
        weaviate_url="test_weaviate_url",
        rate_limit_retry=True,
    )

    assert mock_bolt_app.client.retry_handlers.append.called
    call_args = mock_bolt_app.client.retry_handlers.append.call_args
    assert isinstance(call_args[0][0], RateLimitErrorRetryHandler)


def test_listen(mock_env_variables, mock_weaviate_client, mock_database, mocker):
    chatiq = ChatIQ(
        slack_client_id="test_client_id",
        slack_client_secret="test_client_secret",
        slack_signing_secret="test_signing_secret",
        openai_api_key="test_openai_api_key",
        postgres_url="test_postgres_url",
        weaviate_url="test_weaviate_url",
    )

    mock_event = mocker.patch.object(chatiq.bolt_app, "event")
    mock_action = mocker.patch.object(chatiq.bolt_app, "action")

    chatiq.listen()

    mock_event.assert_has_calls(
        [
            call("message"),
            call("file_shared"),
            call("file_deleted"),
            call("app_mention"),
            call("app_uninstalled"),
            call("app_home_opened"),
            call("channel_deleted"),
            call("group_deleted"),
        ],
        any_order=True,
    )
    mock_action.assert_has_calls(
        [
            call("model_select"),
            call("temperature_select"),
            call("timezone_offset_select"),
            call("context_save"),
        ],
        any_order=True,
    )


def test_add_thread(mock_env_variables, mock_weaviate_client, mock_database, mocker):
    chatiq = ChatIQ(
        slack_client_id="test_client_id",
        slack_client_secret="test_client_secret",
        slack_signing_secret="test_signing_secret",
        openai_api_key="test_openai_api_key",
        postgres_url="test_postgres_url",
        weaviate_url="test_weaviate_url",
    )
    assert len(chatiq.threads) == 0

    mock_thread1 = mocker.MagicMock(spec=threading.Thread)
    mock_thread1.is_alive.return_value = True

    chatiq.add_thread(mock_thread1)
    assert len(chatiq.threads) == 1

    mock_thread1.is_alive.return_value = False

    mock_thread2 = mocker.MagicMock(spec=threading.Thread)
    mock_thread2.is_alive.return_value = True

    chatiq.add_thread(mock_thread2)
    assert len(chatiq.threads) == 1
