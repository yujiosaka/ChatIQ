from chatiq.document_loaders import PlainTextLoader
from chatiq.utils import pretty_json_dumps


def test_check_supported():
    text_file_supported = PlainTextLoader.check_supported({"filetype": "text"})
    assert text_file_supported
    pdf_file_supported = PlainTextLoader.check_supported({"filetype": "pdf"})
    assert not pdf_file_supported
    tombstone_supported = PlainTextLoader.check_supported({"mode": "tombstone"})
    assert not tombstone_supported


def test_plain_text_load_supported_file():
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_id": "C024BE91L",
            "user_id": "U0JD6RZU6",
            "event_ts": "1629470261.000200",
        },
        "event_time": 1629470261,
    }
    file = {
        "id": "F0JD6RZU6",
        "filetype": "python",
        "name": "test.py",
        "title": "Test Python File",
        "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.py",
    }
    loader = PlainTextLoader("print('Hello, world!')", body, file, "public", "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "python",
            "user": "U0JD6RZU6",
            "name": "test.py",
            "title": "Test Python File",
            "channel": "C024BE91L",
            "content": "print('Hello, world!')",
            "page": "1 / 1",
            "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.py",
            "timestamp": "2021-08-20T14:37:41+00:00",
        }
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "F0JD6RZU6",
        "content_type": "python",
        "channel_type": "public",
        "channel_id": "C024BE91L",
        "thread_ts": "0000000000.000000",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.py",
    }


def test_plain_text_load_unsupported_file():
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_id": "C024BE91L",
            "user_id": "U0JD6RZU6",
            "event_ts": "1629470261.000200",
        },
        "event_time": 1629470261,
    }
    file = {
        "id": "F0JD6RZU6",
        "filetype": "unknown",
        "name": "test.unknown",
        "title": "Test Unknown File",
        "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.unknown",
    }
    loader = PlainTextLoader("", body, file, "public", "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 0
