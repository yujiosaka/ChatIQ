import logging
from contextlib import contextmanager

from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table

from chatiq.models import Base


class Database:
    """Manages interactions with the PostgreSQL database.

    This class provides methods to create and manage sessions with the
    database, as well as setting up the necessary tables required for the application.

    Attributes:
        engine (Engine): The SQLAlchemy engine instance connected to the database.
        Session (sessionmaker): The sessionmaker instance that provides database sessions.
        installation_store (SQLAlchemyInstallationStore): The installation store instance for Slack OAuth.
        state_store (SQLAlchemyOAuthStateStore): The state store instance for Slack OAuth.
    """

    STORE_EXPIRATION_SECONDS: int = 600

    def __init__(self, postgres_url: str, slack_client_id: str):
        """Initializes a new instance of the Database class.

        Args:
            postgres_url (str): The connection string for the PostgreSQL database.
            slack_client_id (str): The client ID for the Slack application.
        """

        self.logger = logging.getLogger(__name__)
        self.engine = create_engine(postgres_url)
        self.Session = sessionmaker(bind=self.engine)
        self.installation_store = SQLAlchemyInstallationStore(client_id=slack_client_id, engine=self.engine)
        self.state_store = SQLAlchemyOAuthStateStore(expiration_seconds=self.STORE_EXPIRATION_SECONDS, engine=self.engine)

    @contextmanager
    def transaction(self):
        """Provide a transactional scope around a series of operations.

        Yields:
            Session: The SQLAlchemy session that is used for the transaction.

        Raises:
            Any exceptions that were raised in the block of operations.
            The transaction will be rolled back before the exception is raised.

        Examples:
            >>> with database.transaction() as session:
            >>>     user = User(name="Test User")
            >>>     session.add(user)
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"An error occurred during transaction. Error: {e}")
            raise
        finally:
            session.close()

    def setup(self) -> None:
        """Sets up the necessary tables in the database.

        This includes both the tables required by the application's models and the tables
        required by the Slack OAuth installation and state stores.

        Raises:
            SQLAlchemyError: If there is an issue creating the tables in the database.
        """

        self._setup_base()
        self._setup_stores()

    def _setup_base(self) -> None:
        """Creates the tables required by the application's models in the database.

        This method will attempt to create all tables that don't already exist in the database.

        Raises:
            SQLAlchemyError: If there is an issue creating the tables in the database.
        """

        self.logger.debug("Setup table for models")

        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to setup tables for models. Error: {e}")
            raise

    def _setup_stores(self) -> None:
        """Creates the tables required by the Slack OAuth installation and state stores in the database.

        This method will attempt to create all tables that don't already exist in the database.
        """

        inspector = inspect(self.engine)

        self._create_table_if_not_exists(inspector, self.installation_store.bots)
        self._create_table_if_not_exists(inspector, self.installation_store.installations)
        self._create_table_if_not_exists(inspector, self.state_store.oauth_states)

    def _create_table_if_not_exists(self, inspector: Inspector, table: Table) -> None:
        """Checks if a table exists in the database, and if not, creates it.

        This method uses SQLAlchemy's Inspector to check for the presence of the
        table and Table's `create` method to create it if it doesn't exist.

        Args:
            inspector (Inspector): The SQLAlchemy function to delivers runtime information.
            table (Table): The SQLAlchemy Table object to check/create.

        Raises:
            SQLAlchemyError: If there is an issue creating the table in the database.
        """

        self.logger.debug(f"Creating table '{table.name}' if not exist")

        try:
            if not inspector.has_table(table.name):
                table.create(self.engine)
                self.logger.info(f"Created table '{table.name}'")
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to create table '{table.name}'. Error: {e}")
            raise
