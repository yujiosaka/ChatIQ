from unittest.mock import MagicMock, Mock

import pytest
from freezegun import freeze_time
from langchain.agents.agent import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
from langchain.schema import BaseChatMessageHistory

from chatiq.chat_chain import ChatChain
from chatiq.retriever import Retriever
from chatiq.utils import pretty_json_dumps


@pytest.fixture
def mock_chat_model():
    mock_chat_model = Mock(spec=ChatOpenAI)
    mock_chat_model.model_name = "gpt-3.5-turbo"
    return mock_chat_model


@pytest.fixture
def mock_memory(mocker):
    # Create a mock that includes the chat_memory attribute
    memory_mock = Mock(spec=ConversationTokenBufferMemory)
    memory_mock.chat_memory = mocker.MagicMock(spec=BaseChatMessageHistory)
    return memory_mock


@pytest.fixture
def mock_retriever():
    return Mock(spec=Retriever)


@pytest.fixture
def mock_initialize_agent(mocker):
    # Mock the initialize_agent function
    return mocker.patch("chatiq.chat_chain.initialize_agent", return_value=MagicMock(spec=AgentExecutor))


def test_add_memory_ai_message_with_file_document(mock_chat_model, mock_memory, mock_retriever, mock_initialize_agent):
    chat_chain = ChatChain(
        chat=mock_chat_model,
        memory=mock_memory,
        retriever=mock_retriever,
        bot_id="U06FKAYEHF",
        channel_id="C024BE91L",
        context="Speak like a pirate.",
        timezone_offset="+00:00",
    )
    chat_chain.add_memory_ai_message(
        {
            "user": "U06FKAYEHF",
            "text": "Hello, I'm an AI!",
            "ts": "1652944800.000000",
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
    )

    chat_chain.memory.chat_memory.add_ai_message.assert_called_once_with(
        pretty_json_dumps(
            {
                "user_id": "U06FKAYEHF",
                "action": "Message",
                "action_input": "Hello, I'm an AI!",
                "timestamp": "2022-05-19T07:20:00+00:00",
                "files": [
                    {
                        "title": "Test Python File",
                        "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.py",
                    }
                ],
            }
        )
    )


def test_add_memory_ai_message_with_pdf_document(mock_chat_model, mock_memory, mock_retriever, mock_initialize_agent):
    chat_chain = ChatChain(
        chat=mock_chat_model,
        memory=mock_memory,
        retriever=mock_retriever,
        bot_id="U06FKAYEHF",
        channel_id="C024BE91L",
        context="Speak like a pirate.",
        timezone_offset="+00:00",
    )
    chat_chain.add_memory_ai_message(
        {
            "user": "U06FKAYEHF",
            "text": "Hello, I'm an AI!",
            "ts": "1652944800.000000",
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
        }
    )

    chat_chain.memory.chat_memory.add_ai_message.assert_called_once_with(
        pretty_json_dumps(
            {
                "user_id": "U06FKAYEHF",
                "action": "Message",
                "action_input": "Hello, I'm an AI!",
                "timestamp": "2022-05-19T07:20:00+00:00",
                "files": [
                    {
                        "title": "Test PDF File",
                        "permalink": "https://chatiq.slack.com/files/U0JD6RZU6/F0JD6RZU6/test.pdf",
                    }
                ],
            }
        )
    )


def test_add_memory_user_message_with_unfurling_link(mock_chat_model, mock_memory, mock_retriever, mock_initialize_agent):
    chat_chain = ChatChain(
        chat=mock_chat_model,
        memory=mock_memory,
        retriever=mock_retriever,
        bot_id="U06FKAYEHF",
        channel_id="C024BE91L",
        context="Speak like a pirate.",
        timezone_offset="+00:00",
    )
    chat_chain.add_memory_user_message(
        {
            "user": "U0JD6RZU6",
            "text": "Hello, AI!",
            "ts": "1652944800.000000",
            "attachments": [
                {
                    "id": 1,
                    "original_url": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
                    "author_id": "U0JD6RS3T",
                    "text": "Hello, World!",
                }
            ],
        }
    )

    chat_chain.memory.chat_memory.add_user_message.assert_called_once_with(
        pretty_json_dumps(
            {
                "user_id": "U0JD6RZU6",
                "action": "Message",
                "action_input": "Hello, AI!",
                "timestamp": "2022-05-19T07:20:00+00:00",
                "slack_links": [
                    {
                        "author": "U0JD6RS3T",
                        "content": "Hello, World!",
                        "permalink": "https://chatiq.slack.com/archives/C024BE91L/p1579244331000200",
                    }
                ],
            }
        )
    )


def test_add_memory_user_message_with_slack_link(mock_chat_model, mock_memory, mock_retriever, mock_initialize_agent):
    chat_chain = ChatChain(
        chat=mock_chat_model,
        memory=mock_memory,
        retriever=mock_retriever,
        bot_id="U06FKAYEHF",
        channel_id="C024BE91L",
        context="Speak like a pirate.",
        timezone_offset="+00:00",
    )
    chat_chain.add_memory_user_message({"user": "U0JD6RZU6", "text": "Hello, AI!", "ts": "1652944800.000000"})

    chat_chain.memory.chat_memory.add_user_message.assert_called_once_with(
        pretty_json_dumps(
            {
                "user_id": "U0JD6RZU6",
                "action": "Message",
                "action_input": "Hello, AI!",
                "timestamp": "2022-05-19T07:20:00+00:00",
            }
        )
    )


@freeze_time("2023-05-21 09:00:47.722261")
def test_run(mock_chat_model, mock_memory, mock_retriever, mock_initialize_agent):
    chat_chain = ChatChain(
        chat=mock_chat_model,
        memory=mock_memory,
        retriever=mock_retriever,
        bot_id="U06FKAYEHF",
        channel_id="C024BE91L",
        context="Speak like a pirate.",
        timezone_offset="+00:00",
    )
    chat_chain.run({"user": "U0JD6RZU6", "text": "1 + 1"})

    chat_chain.chain.run.assert_called_once_with(
        input='Human: {\n    "user_id": "U0JD6RZU6",\n    "action": "Message",\n    "action_input": "1 + 1"\n}',
        bot_id="U06FKAYEHF",
        channel_id="C024BE91L",
        time_message="Current time is '2023-05-21T09:00:47.722261+00:00'. ",
        context="Speak like a pirate.",
    )
