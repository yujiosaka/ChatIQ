import uuid

from sqlalchemy import UUID  # type: ignore
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import validates

from chatiq.exceptions import ContextLengthError, ModelSelectError, TemperatureRangeError, TimezoneOffsetSelectError
from chatiq.utils import get_timezone_offsets

from .base import Base


class SlackTeam(Base):
    """Represents a workspace configuration for a Slack team.

    This class is a SQLAlchemy model that represents the configuration of a Slack team
    in the PostgreSQL database.

    Attributes:
        id (Column): The primary key for the table.
        team_id (Column): The unique identifier of the Slack team.
        bot_id (Column): The unique identifier of the bot in the Slack team.
        namespace_uuid (Column): The UUID used as a namespace for generating UUIDs for messages in this team.
        model (Column): The model type to use for the AI (default is "gpt-3.5-turbo").
        temperature (Column): The randomness of the AI's output (default is 1.0).
        context (Column): The context to use for the AI (default is "You are a helpful AI assistant").
        timezone_offset (Column): The default timezone offset for the team (default is "+00:00").
    """

    MODELS = ["gpt-3.5-turbo"]
    TIMEZONE_OFFSETS = get_timezone_offsets()
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0

    __tablename__ = "slack_teams"

    id = Column(Integer, primary_key=True)
    team_id = Column(String(32), unique=True, nullable=False)
    bot_id = Column(String(32), nullable=False)
    namespace_uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    model = Column(String(32), nullable=False, default="gpt-3.5-turbo")
    temperature = Column(Float, nullable=False, default=1.0)
    context = Column(
        String(256),
        nullable=False,
        default=(
            "Assistant is designed to be able to assist with a wide range of tasks, "
            "from answering simple questions to providing in-depth explanations "
            "and discussions on a wide range of topics."
        ),
    )
    timezone_offset = Column(String, nullable=False, default="+00:00")

    @validates("model")
    def validate_model(self, key, model):
        """Validate the model selection for the AI.

        This method checks whether the chosen model is among the accepted models.
        If the model is not in the list of accepted models, it raises a ModelSelectError.

        Args:
            key (str): The key of the column to be validated.
            model (str): The value to be validated.

        Raises:
            ModelSelectError: If the model is not in the list of accepted models.

        Returns:
            str: The validated model.
        """

        if model not in self.MODELS:
            raise ModelSelectError(f"Invalid model: {model}. Must be one of {self.MODELS}")
        return model

    @validates("timezone_offset")
    def validate_timezone_offset(self, key, timezone_offset):
        """Validate the timezone offset.

        This method checks whether the chosen timezone offset is among the accepted offsets.
        If the offset is not in the list of accepted offsets, it raises a TimezoneOffsetSelectError.

        Args:
            key (str): The key of the column to be validated.
            timezone_offset (str): The value to be validated.

        Raises:
            TimezoneOffsetSelectError: If the timezone offset is not in the list of accepted offsets.

        Returns:
            str: The validated timezone offset.
        """

        if timezone_offset not in self.TIMEZONE_OFFSETS:
            raise TimezoneOffsetSelectError(
                f"Invalid timezone_offset: {timezone_offset}. Must be one of {self.TIMEZONE_OFFSETS}"
            )
        return timezone_offset

    @validates("temperature")
    def validate_temperature(self, key, temperature):
        """Validate the temperature value.

        This method checks whether the chosen temperature is within the accepted range.
        If the temperature is not in the accepted range, it raises a TemperatureRangeError.

        Args:
            key (str): The key of the column to be validated.
            temperature (float): The value to be validated.

        Raises:
            TemperatureRangeError: If the temperature is not in the accepted range.

        Returns:
            float: The validated temperature.
        """

        if not self.MIN_TEMPERATURE <= temperature <= self.MAX_TEMPERATURE:
            raise TemperatureRangeError(
                f"Invalid temperature: {temperature}. Must be in range {self.MIN_TEMPERATURE} - {self.MAX_TEMPERATURE}."
            )
        return temperature

    @validates("context")
    def validate_name(self, key, context):
        """Validate the context.

        This method checks whether the length of the context is within the accepted range.
        If the length of the context is too long, it raises a ContextLengthError.

        Args:
            key (str): The key of the column to be validated.
            context (str): The value to be validated.

        Raises:
            ContextLengthError: If the length of the context is too long.

        Returns:
            str: The validated context.
        """

        max_length = self.__table__.c[key].type.length
        if context and len(context) > max_length:
            raise ContextLengthError(f"Invalid context. Must be in less or equal than {max_length} characters.")
        return context
