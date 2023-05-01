import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """A class used to represent the application settings.

    This class is intended to be used as a singleton module, meaning that when it's imported,
    an instance of this class is automatically created and used throughout the application.
    This instance will contain all the application settings as class properties.
    This ensures that there is a single source of truth for settings throughout the application
    and reduces the risk of errors due to inconsistencies in settings.

    Attributes:
        LOG_LEVEL (str): The logging level for the application (default is "info").
        SLACK_CLIENT_ID (str): The client ID for the Slack application.
        SLACK_CLIENT_SECRET (str): The client secret for the Slack application.
        SLACK_SIGNING_SECRET (str): The signing secret for the Slack application.
        OPENAI_API_KEY (str): The API key for the OpenAI application.
        POSTGRES_URL (str): The URL for the PostgreSQL database.
        WEAVIATE_URL (str): The URL for the Weaviate service.
        ENCRYPTION_KEY (bytes): The encryption key for MongoDB.
    """

    @property
    def LOG_LEVEL(self):
        """str: The logging level for the application. Default is "info"."""

        return os.environ.get("LOG_LEVEL", "info").upper()

    @property
    def SLACK_CLIENT_ID(self):
        """str: The client ID for the Slack application."""

        return os.environ.get("SLACK_CLIENT_ID")

    @property
    def SLACK_CLIENT_SECRET(self):
        """str: The client secret for the Slack application."""

        return os.environ.get("SLACK_CLIENT_SECRET")

    @property
    def SLACK_SIGNING_SECRET(self):
        """str: The signing secret for the Slack application."""

        return os.environ.get("SLACK_SIGNING_SECRET")

    @property
    def OPENAI_API_KEY(self):
        """str: The API key for the OpenAI application."""

        return os.environ.get("OPENAI_API_KEY")

    @property
    def POSTGRES_URL(self):
        """str: The URL for the PostgreSQL database."""

        return os.environ.get("POSTGRES_URL")

    @property
    def WEAVIATE_URL(self):
        """str: The URL for the Weaviate service."""

        return os.environ.get("WEAVIATE_URL")


Settings = Settings()
