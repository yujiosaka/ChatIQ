import pytest
import requests_mock
from langchain.document_loaders.parsers.pdf import PyMuPDFParser
from langchain.schema import Document
from slack_bolt import BoltContext

from chatiq.document_loaders import PdfLoader
from chatiq.utils import pretty_json_dumps


@pytest.fixture
def mock_context(mocker):
    mock_context = mocker.MagicMock(spec=BoltContext)
    return mock_context


@pytest.fixture
def mock_request():
    with requests_mock.Mocker() as mock_request:
        yield mock_request


@pytest.fixture
def mock_parser(mocker):
    mock_parser = mocker.MagicMock(spec=PyMuPDFParser)
    mock_parser.parse.return_value = [Document(page_content="parsed pdf content", metadata={"page": 1})]
    mocker.patch("chatiq.document_loaders.pdf.PyMuPDFParser", return_value=mock_parser)
    return mock_parser


def test_check_supported():
    pdf_file_supported = PdfLoader.check_supported({"filetype": "pdf"})
    assert pdf_file_supported
    text_file_supported = PdfLoader.check_supported({"filetype": "text"})
    assert not text_file_supported
    tombstone_supported = PdfLoader.check_supported({"mode": "tombstone"})
    assert not tombstone_supported


def test_pdf_load_supported_file(mock_context, mock_request, mock_parser):
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
        "filetype": "pdf",
        "name": "test.pdf",
        "title": "Test PDF File",
        "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.pdf",
        "url_private": "http://example.com/test.pdf",
    }
    mock_request.get("http://example.com/test.pdf", text="pdf content")

    loader = PdfLoader(mock_context, body, file, "public", "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].page_content == pretty_json_dumps(
        {
            "content_type": "pdf",
            "user": "U0JD6RZU6",
            "name": "test.pdf",
            "title": "Test PDF File",
            "channel": "C024BE91L",
            "content": "parsed pdf content",
            "page": "1 / 1",
            "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.pdf",
            "timestamp": "2021-08-20T14:37:41+00:00",
        }
    )
    assert documents[0].metadata == {
        "file_or_attachment_id": "F0JD6RZU6",
        "content_type": "pdf",
        "channel_type": "public",
        "channel_id": "C024BE91L",
        "thread_ts": "0000000000.000000",
        "ts": "1629470261.000200",
        "timestamp": "2021-08-20T14:37:41+00:00",
        "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.pdf",
    }


def test_pdf_load_unsupported_file(mock_context):
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

    loader = PdfLoader(mock_context, body, file, "public", "gpt-3.5-turbo")
    documents = loader.load()

    assert len(documents) == 0
