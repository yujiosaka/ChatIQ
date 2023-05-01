from chatiq.document_loaders import UnfurlingLinkLoader
from chatiq.utils import pretty_json_dumps


def test_check_supported():
    unfurling_link_supported = UnfurlingLinkLoader.check_supported(
        {
            "id": 1,
            "original_url": "https://example.com",
            "title": "Example Domain",
            "text": "This domain is for use in illustrative examples in documents.",
        }
    )
    assert unfurling_link_supported
    non_unfurling_link_supported = UnfurlingLinkLoader.check_supported(
        {
            "id": 1,
            "original_url": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
            "author_id": "U0JD6RS3T",
            "text": "Hello, World!",
        }
    )
    assert not non_unfurling_link_supported


def test_unfurling_link_loader_load_valid_input():
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
        "original_url": "https://example.com",
        "title": "Example Domain",
        "text": "This domain is for use in illustrative examples in documents.",
    }
    model = "gpt-3.5-turbo"

    loader = UnfurlingLinkLoader(body, message, attachment, model)
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "unfurling_link",
            "user": "U0JD6RZU6",
            "title": "Example Domain",
            "channel": "C024BE91L",
            "content": "This domain is for use in illustrative examples in documents.",
            "permalink": "https://example.com",
            "timestamp": "2021-08-20T14:37:41+00:00",
        },
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "1629470261.000200-1",
        "content_type": "unfurling_link",
        "channel_type": "channel",
        "channel_id": "C024BE91L",
        "thread_ts": "0000000000.000000",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://example.com",
    }


def test_unfurling_link_loader_load_invalid_input():
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
    attachment = {"id": None, "original_url": None, "title": None, "text": None}
    model = "gpt-3.5-turbo"

    loader = UnfurlingLinkLoader(body, message, attachment, model)
    documents = loader.load()

    assert len(documents) == 0
