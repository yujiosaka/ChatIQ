from langchain.vectorstores import Weaviate
from langchain.vectorstores.base import VectorStoreRetriever


class Retriever(VectorStoreRetriever):
    is_private: bool
    channel_id: str

    """A class that retrieves documents from the Weaviate index based on certain conditions.

    The Retriever provides a way to fetch documents from the Weaviate index. The conditions for
    retrieval vary based on whether the channel is private or public.

    Attributes:
        vectorstore (Weaviate): A Weaviate instance to interact with the Weaviate class.
        is_private (bool): True if the channel is private, False otherwise.
        channel_id (str): The ID of the channel where the bot was mentioned.
        thread_ts (str): The ID of the thread. This is used to exclude messages in the current thread.
    """

    def __init__(self, vectorstore: Weaviate, is_private: bool, channel_id: str, thread_ts: str):
        """Initializes a Retriever instance for a specific team and channel.

        Args:
            vectorstore (Weaviate): A Weaviate instance to interact with the Weaviate class.
            is_private (bool): True if the channel is private, False otherwise.
            channel_id (str): The ID of the channel where the bot was mentioned.
            thread_ts (str): The ID of the thread. This is used to exclude messages in the current thread.
        """

        where_filter = self._build_retrieval_where_filter(is_private, channel_id, thread_ts)
        super().__init__(
            vectorstore=vectorstore,
            search_kwargs={"where_filter": where_filter},
            is_private=is_private,
            channel_id=channel_id,
        )

    def search_url(self, url: str) -> str:
        """Search for a specific URL in the Weaviate index.

        This method builds a URL-specific filter and retrieves documents from the Weaviate index that match
        this filter. If the document is found, it returns the content of the first matching document.

        Args:
            url (str): The URL to search for.

        Returns:
            str: The content of the first document matching the URL.
        """

        where_filter = self._build_url_search_where_filter(self.is_private, self.channel_id, url)
        result = (
            self.vectorstore._client.query.get(self.vectorstore._index_name, self.vectorstore._query_attrs)
            .with_where(where_filter)
            .with_limit(1)
            .do()
        )

        documents = result["data"]["Get"][self.vectorstore._index_name]
        if documents:
            return documents[0]["content"]

        return "Document is not found."

    def _build_retrieval_where_filter(self, is_private: bool, channel_id: str, thread_ts: str) -> dict:
        """Builds a filter for retrieving documents based on whether the channel is private or public.

        Args:
            is_private (bool): True if the channel is private, False otherwise.
            channel_id (str): The ID of the channel where the bot was mentioned.
            thread_ts (str): The ID of the thread. This is used to exclude messages in the current thread.

        Returns:
            dict: A filter to be used for document retrieval.
        """

        if is_private:
            return self._build_retrieval_private_where_filter(channel_id, thread_ts)
        else:
            return self._build_retrieval_public_where_filter(thread_ts)

    def _build_retrieval_private_where_filter(self, channel_id: str, thread_ts: str) -> dict:
        """Builds a filter for retrieving documents from a private channel.

        Args:
            channel_id (str): The ID of the private channel where the bot was mentioned.
            thread_ts (str): The ID of the thread. This is used to exclude messages in the current thread.

        Returns:
            dict: A filter to be used for document retrieval.
        """

        return {
            "operator": "And",
            "operands": [
                {
                    "path": ["thread_ts"],
                    "operator": "NotEqual",
                    "valueString": thread_ts,
                },
                {
                    "operator": "Or",
                    "operands": [
                        {"path": ["channel_id"], "operator": "Equal", "valueString": channel_id},
                        {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                    ],
                },
            ],
        }

    def _build_retrieval_public_where_filter(self, thread_ts: str) -> dict:
        """Builds a filter for retrieving documents from a public channel.

        Args:
            thread_ts (str): The ID of the thread. This is used to exclude messages in the current thread.

        Returns:
            dict: A filter to be used for document retrieval.
        """

        return {
            "operator": "And",
            "operands": [
                {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                {
                    "path": ["thread_ts"],
                    "operator": "NotEqual",
                    "valueString": thread_ts,
                },
            ],
        }

    def _build_url_search_where_filter(self, is_private: bool, channel_id: str, url: str) -> dict:
        """Builds a filter for URL search based on whether the channel is private or public.

        Args:
            is_private (bool): True if the channel is private, False otherwise.
            channel_id (str): The ID of the channel where the bot was mentioned.
            URL (str): The URL to search for.

        Returns:
            dict: A filter to be used for document url_search.
        """

        if is_private:
            return self._build_url_search_private_where_filter(channel_id, url)
        else:
            return self._build_url_search_public_where_filter(url)

    def _build_url_search_private_where_filter(self, channel_id: str, url: str) -> dict:
        """Builds a filter for URL search from a private channel.

        Args:
            channel_id (str): The ID of the private channel where the bot was mentioned.
            URL (str): The URL to search for.

        Returns:
            dict: A filter to be used for document URL search.
        """

        return {
            "operator": "And",
            "operands": [
                {
                    "path": ["permalink"],
                    "operator": "Equal",
                    "valueString": url,
                },
                {
                    "operator": "Or",
                    "operands": [
                        {"path": ["channel_id"], "operator": "Equal", "valueString": channel_id},
                        {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                    ],
                },
            ],
        }

    def _build_url_search_public_where_filter(self, url: str) -> dict:
        """Builds a filter for URL search from a public channel.

        Args:
            URL (str): The URL to search for.

        Returns:
            dict: A filter to be used for document URL search.
        """

        return {
            "operator": "And",
            "operands": [
                {"path": ["channel_type"], "operator": "Equal", "valueString": "channel"},
                {"path": ["permalink"], "operator": "Equal", "valueString": url},
            ],
        }
