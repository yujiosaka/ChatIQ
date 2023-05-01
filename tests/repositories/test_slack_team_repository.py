import pytest
from sqlalchemy.exc import NoResultFound

from chatiq.models import SlackTeam
from chatiq.repositories import SlackTeamRepository


@pytest.fixture
def mock_session(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_team(mocker):
    return mocker.MagicMock(spec=SlackTeam)


def test_init(mock_session):
    repository = SlackTeamRepository(mock_session)
    assert repository.session is mock_session


def test_get_exists(mock_session, mock_team):
    mock_session.query().filter_by().one.return_value = mock_team

    repository = SlackTeamRepository(mock_session)
    team = repository.get(mock_team.team_id)

    assert team.team_id == mock_team.team_id


def test_get_not_exists(mock_session, mock_team):
    mock_session.query().filter_by().one.side_effect = NoResultFound()

    repository = SlackTeamRepository(mock_session)

    with pytest.raises(ValueError):
        repository.get(mock_team.team_id)


def test_get_or_create_exists(mock_session, mock_team):
    mock_session.query().filter_by().first.return_value = mock_team

    repository = SlackTeamRepository(mock_session)
    team = repository.get_or_create(mock_team.team_id, mock_team.bot_id)

    assert team.team_id == mock_team.team_id
    assert team.bot_id == mock_team.bot_id
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_get_or_create_not_exists(mock_session, mock_team):
    mock_session.query().filter_by().first.return_value = None

    repository = SlackTeamRepository(mock_session)
    team = repository.get_or_create(mock_team.team_id, mock_team.bot_id)

    assert team.team_id == mock_team.team_id
    assert team.bot_id == mock_team.bot_id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_update(mock_session, mock_team):
    model = mock_team.model
    mock_team.model = None
    mock_session.query().filter_by().one.return_value = mock_team

    repository = SlackTeamRepository(mock_session)
    team = repository.update(mock_team.team_id, {"model": model})

    assert team.id == mock_team.id
    assert team.model == model
    mock_session.commit.assert_called_once()


def test_delete(mock_session, mock_team):
    repository = SlackTeamRepository(mock_session)
    repository.delete(mock_team.team_id)

    mock_session.query.return_value.filter.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()
