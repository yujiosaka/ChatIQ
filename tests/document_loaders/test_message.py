import pytest
from slack_sdk import WebClient

from chatiq.document_loaders import MessageLoader
from chatiq.utils import pretty_json_dumps


@pytest.fixture
def mock_client(mocker):
    mock_client = mocker.MagicMock(spec=WebClient)
    mock_client.chat_getPermalink.return_value = {
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200"
    }
    return mock_client


def test_message_loader_load_new_message(mock_client):
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "text": "Hello, World!",
            "thread_ts": "1629470261.000200",
            "ts": "1629470261.000200",
        },
        "event_time": 1629470261,
    }

    loader = MessageLoader(mock_client, body, body["event"], "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "message",
            "user": "U0JD6RZU6",
            "channel": "C024BE91L",
            "message": "Hello, World!",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
            "timestamp": "2021-08-20T14:37:41+00:00",
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "",
        "content_type": "message",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "1629470261.000200",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
    }


def test_message_loader_load_message_changed(mock_client):
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "type": "message",
            "subtype": "message_changed",
            "channel": "C024BE91L",
            "channel_type": "channel",
            "message": {
                "user": "U0JD6RZU6",
                "text": "Hello, World! (edited)",
                "thread_ts": "1629470261.000200",
                "ts": "1629470261.000200",
            },
        },
        "event_time": 1629470261,
    }

    loader = MessageLoader(mock_client, body, body["event"]["message"], "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "message",
            "user": "U0JD6RZU6",
            "channel": "C024BE91L",
            "message": "Hello, World! (edited)",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
            "timestamp": "2021-08-20T14:37:41+00:00",
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "",
        "content_type": "message",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "1629470261.000200",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
    }


def test_message_loader_load_file_documents(mock_client):
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "text": "Hello, World!",
            "thread_ts": "1629470261.000200",
            "ts": "1629470261.000200",
            "files": [
                {
                    "id": "F0JD6RZU6",
                    "filetype": "python",
                    "name": "test.py",
                    "title": "Test Python File",
                    "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.py",
                    "timestamp": 1629470261.0002,
                }
            ],
        },
        "event_time": 1629470261,
    }

    loader = MessageLoader(mock_client, body, body["event"], "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "message",
            "user": "U0JD6RZU6",
            "channel": "C024BE91L",
            "message": "Hello, World!",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
            "timestamp": "2021-08-20T14:37:41+00:00",
            "files": [
                {
                    "title": "Test Python File",
                    "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.py",
                }
            ],
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "",
        "content_type": "message",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "1629470261.000200",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
    }


def test_message_loader_load_pdf_documents(mock_client):
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "text": "Hello, World!",
            "thread_ts": "1629470261.000200",
            "ts": "1629470261.000200",
            "files": [
                {
                    "id": "F0JD6RZU6",
                    "filetype": "pdf",
                    "name": "test.pdf",
                    "title": "Test PDF File",
                    "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.pdf",
                    "timestamp": 1629470261.0002,
                }
            ],
        },
        "event_time": 1629470261,
    }

    loader = MessageLoader(mock_client, body, body["event"], "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "message",
            "user": "U0JD6RZU6",
            "channel": "C024BE91L",
            "message": "Hello, World!",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
            "timestamp": "2021-08-20T14:37:41+00:00",
            "files": [
                {
                    "title": "Test PDF File",
                    "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.pdf",
                }
            ],
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "",
        "content_type": "message",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "1629470261.000200",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
    }


def test_message_loader_unfurling_links(mock_client):
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "text": "Hello, World!",
            "thread_ts": "1629470261.000200",
            "ts": "1629470261.000200",
            "attachments": [
                {
                    "id": 1,
                    "fallback": "Required plain-text summary of the attachment.",
                    "text": "Optional text that appears within the attachment",
                    "title": "Optional title",
                    "original_url": "http://example.com/path",
                }
            ],
        },
        "event_time": 1629470261,
    }

    loader = MessageLoader(mock_client, body, body["event"], "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "message",
            "user": "U0JD6RZU6",
            "channel": "C024BE91L",
            "message": "Hello, World!",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
            "timestamp": "2021-08-20T14:37:41+00:00",
            "unfurling_links": [
                {
                    "title": "Optional title",
                    "permalink": "http://example.com/path",
                }
            ],
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "",
        "content_type": "message",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "1629470261.000200",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
    }


def test_message_loader_slack_links(mock_client):
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "text": "Hello, World!",
            "thread_ts": "1629470261.000200",
            "ts": "1629470261.000200",
            "attachments": [
                {
                    "id": 1,
                    "original_url": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
                    "author_id": "U0JD6RS3T",
                    "text": "Hello, World!",
                }
            ],
        },
        "event_time": 1629470261,
    }

    loader = MessageLoader(mock_client, body, body["event"], "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "message",
            "user": "U0JD6RZU6",
            "channel": "C024BE91L",
            "message": "Hello, World!",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
            "timestamp": "2021-08-20T14:37:41+00:00",
            "slack_links": [
                {
                    "author": "U0JD6RS3T",
                    "content": "Hello, World!",
                    "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
                }
            ],
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "",
        "content_type": "message",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "1629470261.000200",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1629470261000200",
    }
