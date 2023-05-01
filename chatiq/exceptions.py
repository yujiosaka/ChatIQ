class SettingsValidationError(ValueError):
    """Exception raised when required settings are missing."""

    pass


class ModelSelectError(ValueError):
    """Exception raised for errors in the model select."""

    pass


class TemperatureRangeError(ValueError):
    """Exception raised for errors in the input temperature range."""

    pass


class TimezoneOffsetSelectError(ValueError):
    """Exception raised for errors in the timezone offset select."""

    pass


class ContextLengthError(ValueError):
    """Exception raised for errors in the context length."""

    pass
