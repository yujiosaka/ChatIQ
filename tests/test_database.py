import pytest
from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
from sqlalchemy import MetaData, Table
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import sessionmaker

from chatiq.database import Database


@pytest.fixture
def mock_create_engine(mocker):
    return mocker.patch("chatiq.database.create_engine", return_value=mocker.MagicMock())


@pytest.fixture
def mock_sessionmaker(mocker):
    mock_sessionmaker = mocker.MagicMock(spec=sessionmaker)
    mocker.patch("chatiq.database.sessionmaker", return_value=mock_sessionmaker)
    return mock_sessionmaker


@pytest.fixture
def mock_installation_store(mocker):
    mock_installation_store = mocker.MagicMock(spec=SQLAlchemyInstallationStore)
    mock_installation_store.bots = mocker.MagicMock(spec=Table)
    mock_installation_store.bots.name = "slack_bots"
    mock_installation_store.installations = mocker.MagicMock(spec=Table)
    mock_installation_store.installations.name = "slack_installations"
    mocker.patch("chatiq.database.SQLAlchemyInstallationStore", return_value=mock_installation_store)
    return mock_installation_store


@pytest.fixture
def mock_state_store(mocker):
    mock_state_store = mocker.MagicMock(spec=SQLAlchemyOAuthStateStore)
    mock_state_store.oauth_states = mocker.MagicMock(spec=Table)
    mock_state_store.oauth_states.name = "slack_oauth_states"
    mocker.patch("chatiq.database.SQLAlchemyOAuthStateStore", return_value=mock_state_store)
    return mock_state_store


@pytest.fixture
def mock_inspector(mocker):
    inspector = mocker.MagicMock(spec=Inspector)
    mocker.patch("chatiq.database.inspect", return_value=inspector)
    return inspector


@pytest.fixture
def mock_base_metadata_create_all(mocker):
    return mocker.patch.object(MetaData, "create_all")


def test_setup_when_table_exists(
    mock_create_engine,
    mock_sessionmaker,
    mock_installation_store,
    mock_state_store,
    mock_inspector,
    mock_base_metadata_create_all,
):
    mock_inspector.has_table.return_value = True

    db = Database("postgres-url", "slack-client-id")
    db.setup()

    mock_base_metadata_create_all.assert_called_once()
    assert mock_inspector.has_table.call_count == 3
    assert mock_installation_store.bots.create.call_count == 0
    assert mock_installation_store.installations.create.call_count == 0
    assert mock_state_store.oauth_states.create.call_count == 0


def test_setup_when_table_not_exists(
    mock_create_engine,
    mock_sessionmaker,
    mock_installation_store,
    mock_state_store,
    mock_inspector,
    mock_base_metadata_create_all,
):
    mock_inspector.has_table.return_value = False

    db = Database("postgres-url", "slack-client-id")
    db.setup()

    mock_base_metadata_create_all.assert_called_once()
    assert mock_inspector.has_table.call_count == 3
    assert mock_installation_store.bots.create.call_count == 1
    assert mock_installation_store.installations.create.call_count == 1
    assert mock_state_store.oauth_states.create.call_count == 1


def test_transaction_commit(
    mock_create_engine,
    mock_sessionmaker,
    mock_installation_store,
    mock_state_store,
    mock_inspector,
):
    db = Database("postgres-url", "slack-client-id")
    with db.transaction():
        pass

    mock_sessionmaker.return_value.commit.assert_called_once()
    mock_sessionmaker.return_value.rollback.assert_not_called()
    mock_sessionmaker.return_value.close.assert_called_once()


def test_transaction_rollback(
    mock_create_engine,
    mock_sessionmaker,
    mock_installation_store,
    mock_state_store,
    mock_inspector,
):
    db = Database("postgres-url", "slack-client-id")
    with pytest.raises(Exception):
        with db.transaction():
            raise Exception()

    mock_sessionmaker.return_value.commit.assert_not_called()
    mock_sessionmaker.return_value.rollback.assert_called_once()
    mock_sessionmaker.return_value.close.assert_called_once()
