import pytest
from langchain_community.vectorstores import Weaviate
from weaviate import Client
from weaviate.gql import Query

from chatiq.retriever import Retriever


@pytest.fixture
def mock_vectorstore(mocker):
    mock_vectorstore = mocker.MagicMock(spec=Weaviate)
    mock_vectorstore._index_name = "Messageteam_id1"
    mock_vectorstore._query_attrs = ["content"]
    mock_vectorstore._client = mocker.MagicMock(spec=Client)
    mock_vectorstore._client.query = mocker.MagicMock(spec=Query)
    return mock_vectorstore


@pytest.mark.parametrize(
    "is_private,expected_filter",
    [
        (
            True,
            {
                "operator": "And",
                "operands": [
                    {
                        "path": ["thread_ts"],
                        "operator": "NotEqual",
                        "valueString": "1629470261.000200",
                    },
                    {
                        "operator": "Or",
                        "operands": [
                            {"path": ["channel_id"], "operator": "Equal", "valueString": "T0JD6RZU6"},
                            {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                        ],
                    },
                ],
            },
        ),
        (
            False,
            {
                "operator": "And",
                "operands": [
                    {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                    {
                        "path": ["thread_ts"],
                        "operator": "NotEqual",
                        "valueString": "1629470261.000200",
                    },
                ],
            },
        ),
    ],
)
def test_retriever_initialization(is_private, expected_filter, mock_vectorstore):
    retriever = Retriever(mock_vectorstore, is_private, "T0JD6RZU6", "1629470261.000200")
    assert retriever.search_kwargs["where_filter"] == expected_filter


@pytest.mark.parametrize(
    "is_private,expected_filter",
    [
        (
            True,
            {
                "operator": "And",
                "operands": [
                    {
                        "path": ["permalink"],
                        "operator": "Equal",
                        "valueString": "https://example.com",
                    },
                    {
                        "operator": "Or",
                        "operands": [
                            {"path": ["channel_id"], "operator": "Equal", "valueString": "T0JD6RZU6"},
                            {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                        ],
                    },
                ],
            },
        ),
        (
            False,
            {
                "operator": "And",
                "operands": [
                    {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                    {
                        "path": ["permalink"],
                        "operator": "Equal",
                        "valueString": "https://example.com",
                    },
                ],
            },
        ),
    ],
)
def test_search_url(is_private, expected_filter, mock_vectorstore):
    mock_vectorstore._client.query.get.return_value.with_where.return_value.with_limit.return_value.do.return_value = {
        "data": {"Get": {mock_vectorstore._index_name: [{"content": "Test content"}]}}
    }

    retriever = Retriever(mock_vectorstore, is_private, "T0JD6RZU6", "1629470261.000200")
    result = retriever.search_url("https://example.com")

    mock_vectorstore._client.query.get.assert_called_once_with(mock_vectorstore._index_name, mock_vectorstore._query_attrs)
    mock_vectorstore._client.query.get.return_value.with_where.assert_called_once_with(expected_filter)
    mock_vectorstore._client.query.get.return_value.with_where.return_value.with_limit.assert_called_once_with(1)
    assert result == "Test content"
