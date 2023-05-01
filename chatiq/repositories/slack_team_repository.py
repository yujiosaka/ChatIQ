import logging

from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session

from chatiq.models import SlackTeam


class SlackTeamRepository:
    """Handles interactions with the SlackTeam model in the database.

    Args:
        session (Session): The SQLAlchemy session to use for database interactions.

    Attributes:
        session (Session): The SQLAlchemy session to use for database interactions.
    """

    def __init__(self, session: Session):
        """Initializes a new instance of the SlackTeamRepository.

        Args:
            session (Session): The SQLAlchemy session to use for database interactions.
        """

        self.logger = logging.getLogger(__name__)
        self.session = session

    def get(self, team_id: str) -> SlackTeam:
        """Retrieve a SlackTeam.

        Args:
            team_id (str): The Slack team ID of the SlackTeam to retrieve.

        Returns:
            SlackTeam: The retrieved SlackTeam.

        Raises:
            ValueError: If no SlackTeam exists with the provided team ID.
        """

        self.logger.debug(f"Attempting to find team: {team_id}")

        try:
            return self.session.query(SlackTeam).filter_by(team_id=team_id).one()
        except NoResultFound as e:
            error_message = f"Team {team_id} not found: {e}"
            self.logger.error(error_message)
            raise ValueError(error_message)
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to find team: {team_id}. Error: {e}")
            raise

    def get_or_create(self, team_id: str, bot_id: str) -> SlackTeam:
        """Retrieve an existing SlackTeam or create a new one if it doesn't exist.

        Args:
            team_id (str): The Slack team ID of the SlackTeam to get or create.

        Returns:
            SlackTeam: The retrieved or created SlackTeam.
        """

        self.logger.debug(f"Attempting to get or create team: {team_id}")

        try:
            team = self.session.query(SlackTeam).filter_by(team_id=team_id).first()
            if team is None:
                team = SlackTeam(team_id=team_id, bot_id=bot_id)
                self.session.add(team)
                self.session.commit()
                self.logger.info(f"Created team: {team_id}")
            return team
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get or create team: {team_id}. Error: {e}")
            raise

    def update(self, team_id: str, attributes: dict) -> SlackTeam:
        """Update the specified attributes of a SlackTeam.

        Args:
            team_id (str): The Slack team ID of the SlackTeam to update.
            attributes (dict): A dictionary where keys are attribute names and values are the new attribute values.

        Raises:
            ValueError: If an invalid attribute name is provided.
        """
        self.logger.debug(f"Attempting to update attributes of team: {team_id}")

        try:
            team = self.get(team_id)
            for field, value in attributes.items():
                if hasattr(team, field):
                    setattr(team, field, value)
                else:
                    raise ValueError(f"Invalid field {field} for team")
            self.session.commit()
            self.logger.info(f"Successfully updated attributes of team: {team_id}")
            return team
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to update attributes of team: {team_id}. Error: {e}")
            raise

    def delete(self, team_id: str) -> None:
        """Deletes the Slack team with the given team_id from the database.

        Args:
            team_id (str): The ID of the team to be deleted.
        """
        self.logger.debug(f"Deleting team: {team_id}")

        try:
            delete_count = self.session.query(SlackTeam).filter(SlackTeam.team_id == team_id).delete()
            self.session.commit()

            if delete_count:
                self.logger.info(f"Deleted team: {team_id}")

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to delete team: {team_id}. Error: {e}")
            raise
