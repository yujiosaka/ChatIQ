from typing import Optional

import tiktoken


class TextProcessor:
    """A class that processes text based on a specific language model.

    This class provides a way to truncate text by a specified number of tokens. It
    uses the specified model to tokenize the text, and then trims it to the required length.
    After trimming, the tokens are decoded back into a string. It also provides a way
    to fetch the token length for a given model.

    Attributes:
        model (str): The name of the model used for tokenization.

    Raises:
        KeyError: If the provided model is not supported.
    """

    MODEL_TO_TOKEN_LENGTH = {
        "gpt-4": 6000,
        "gpt-4-0314": 6000,
        "gpt-4-32k": 30000,
        "gpt-4-32k-0314": 30000,
        "gpt-3.5-turbo": 3000,
        "gpt-3.5-turbo-0301": 3000,
    }

    def __init__(self, model: str) -> None:
        """
        Initializes TextProcessor with the model.

        Args:
            model (str): The name of the model used for tokenization.
        """
        if model not in self.MODEL_TO_TOKEN_LENGTH:
            raise KeyError(f"The model '{model}' is not supported.")
        self.model = model

    @classmethod
    def get_token_length_for_model(cls, model: str) -> int:
        """Returns the maximum token length for the provided model.

        Args:
            model (str): The name of the model.

        Returns:
            int: The maximum token length for the model.

        Raises:
            KeyError: If the provided model is not supported.
        """

        if model not in cls.MODEL_TO_TOKEN_LENGTH:
            raise KeyError(f"The model '{model}' is not supported.")
        return cls.MODEL_TO_TOKEN_LENGTH[model]

    def truncate_text(self, text: str, length: Optional[int] = None) -> str:
        """
        Truncates the text to a specified number of tokens.

        Args:
            text (str): The text to truncate.
            length (Optional[int]): The number of tokens to which the text should be truncated.

        Returns:
            str: The truncated text.
        """

        encoding = tiktoken.encoding_for_model(self.model)
        tokens = encoding.encode(text)
        if length is None:
            length = self.get_token_length_for_model(self.model)

        truncated_text = encoding.decode(tokens[: length - 1])
        if len(truncated_text) == len(text):
            return text

        return f"{truncated_text}..."
