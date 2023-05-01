from chatiq.document_loaders import SlackLinkLoader
from chatiq.utils import pretty_json_dumps


def test_check_supported():
    slack_link_supported = SlackLinkLoader.check_supported(
        {
            "id": 1,
            "original_url": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
            "author_id": "U0JD6RS3T",
            "text": "Hello, World!",
        }
    )
    assert slack_link_supported
    non_slack_link_supported = SlackLinkLoader.check_supported(
        {
            "id": 1,
            "original_url": "https://example.com",
            "title": "Example Domain",
            "text": "This domain is for use in illustrative examples in documents.",
        }
    )
    assert not non_slack_link_supported


def test_slack_link_loader_load_valid_input():
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "ts": "1629470261.000200",
        },
        "event_time": 1629470261,
    }
    message = body["event"]
    attachment = {
        "id": 1,
        "original_url": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
        "author_id": "U0JD6RS3T",
        "text": "Hello, World!",
    }
    model = "gpt-3.5-turbo"

    loader = SlackLinkLoader(body, message, attachment, model)
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "slack_link",
            "user": "U0JD6RZU6",
            "author": "U0JD6RS3T",
            "channel": "C024BE91L",
            "content": "Hello, World!",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
            "timestamp": "2021-08-20T14:37:41+00:00",
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "1629470261.000200-1",
        "content_type": "slack_link",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "0000000000.000000",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
    }


def test_slack_link_loader_load_file_document():
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "ts": "1629470261.000200",
        },
        "event_time": 1629470261,
    }
    message = body["event"]
    attachment = {
        "id": 1,
        "original_url": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
        "author_id": "U0JD6RS3T",
        "text": "Hello, World!",
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
    }
    model = "gpt-3.5-turbo"

    loader = SlackLinkLoader(body, message, attachment, model)
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "slack_link",
            "user": "U0JD6RZU6",
            "author": "U0JD6RS3T",
            "channel": "C024BE91L",
            "content": "Hello, World!",
            "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
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
        "file_or_attachment_id": "1629470261.000200-1",
        "content_type": "slack_link",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "0000000000.000000",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
    }


def test_slack_link_loader_load_invalid_input():
    body = {
        "team_id": "T0JD6RZU6",
        "event": {
            "channel_type": "channel",
            "channel": "C024BE91L",
            "user": "U0JD6RZU6",
            "ts": "1629470261.000200",
        },
        "event_time": 1629470261,
    }
    message = body["event"]
    attachment = {"id": None, "original_url": None, "author_id": None, "text": None}
    model = "gpt-3.5-turbo"

    loader = SlackLinkLoader(body, message, attachment, model)
    documents = loader.load()

    assert len(documents) == 0
