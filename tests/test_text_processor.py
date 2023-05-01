import pytest

from chatiq.text_processor import TextProcessor


def test_truncate_text_unsupported_model():
    with pytest.raises(KeyError):
        TextProcessor("unsupported-model")


def test_get_token_length_for_unsupported_model():
    with pytest.raises(KeyError):
        TextProcessor.get_token_length_for_model("unsupported-model")


def test_get_token_length_for_model():
    token_length = TextProcessor.get_token_length_for_model("gpt-3.5-turbo")

    assert token_length == 3000


def test_truncate_text_short_length():
    processor = TextProcessor("gpt-3.5-turbo")
    token_count = processor.truncate_text("こんにちは、世界！", 2)

    assert token_count == "こんにちは..."


def test_truncate_text_default_length():
    processor = TextProcessor("gpt-3.5-turbo")
    token_count = processor.truncate_text("こんにちは、世界！")

    assert token_count == "こんにちは、世界！"
