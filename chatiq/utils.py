import json
import re
from datetime import datetime
from typing import Any, List, Optional

from dateutil.tz import tzoffset
from langchain.docstore.document import Document
from pytz import UTC, common_timezones, timezone

JSON_INDENT_LEVEL = 4


def extract_emoji_text(text: str, emoji_pattern: str) -> Optional[str]:
    """Extracts the text associated with a specific emoji in a given text string.

    Args:
        text (str): The text string to extract the emoji text from.
        emoji_pattern (str): The emoji pattern to look for.

    Returns:
        Optional[str]: The text associated with the emoji.
    """

    next_emoji_pattern = r":[^\s:]+:"
    emoji_regex = rf"(?:^|\n){emoji_pattern}(.*?)(?=\n{next_emoji_pattern}|$)"
    extracted_texts = re.findall(emoji_regex, text, re.DOTALL)

    if not extracted_texts:
        return None

    return extracted_texts[0].strip()


def format_mention(user_id: str) -> str:
    """Formats a user ID into a mention string for Slack.

    Args:
        user_id (str): The user ID to format.

    Returns:
        str: The formatted mention string.

    Raises:
        ValueError: If the provided user_id is invalid.
    """

    if not user_id:
        raise ValueError(f"Invalid user_id format: {user_id}")

    return f"<@{user_id}>"


def get_timezone_offsets() -> List[str]:
    """Returns a sorted list of unique timezone offsets from pytz common timezones.

    Returns:
        List[str]: A sorted list of unique timezone offsets.
    """

    offset_minutes_set = set()
    for tz in common_timezones:
        tzinfo = timezone(tz)
        now_tz = datetime.utcnow().replace(tzinfo=UTC).astimezone(tzinfo)
        utcoffset = now_tz.utcoffset()
        if utcoffset is None:
            raise ValueError(f"Unexpected None value from utcoffset for timezone: {tz}")

        offset_seconds = utcoffset.total_seconds()
        offset_minutes, _ = divmod(offset_seconds, 60)
        offset_minutes_set.add(offset_minutes)

    sorted_offset_minutes = sorted(list(offset_minutes_set))

    offsets = []
    for offset_minutes in sorted_offset_minutes:
        offset_hours, offset_minutes = divmod(offset_minutes, 60)
        if offset_minutes not in [0, 30]:
            continue

        if offset_hours < 0 and offset_minutes > 0:
            offset_hours += 1
            offset_minutes = 60 - offset_minutes

        offset = f"{int(offset_hours):+03}:{int(offset_minutes):02}"
        offsets.append(offset)

    return offsets


def get_emoji_from_timezone_offset(timezone_offset: str) -> str:
    """Returns an emoji associated with the given timezone offset.

    Args:
        timezone_offset (str): The timezone offset in "+HH:MM" or "-HH:MM" format.

    Returns:
        str: The associated emoji in unicode.
    """

    offset_parts = timezone_offset.split(":")
    offset_hours, offset_minutes = map(int, offset_parts)

    if offset_hours < 0 and offset_minutes == 30:
        offset_hours -= 1

    emoji_hours = (offset_hours + 12) % 12

    if offset_minutes == 30:
        return f":clock{emoji_hours}30:"
    else:
        return f":clock{emoji_hours if emoji_hours != 0 else 12}:"


def utc_to_local(utc_datetime: datetime, timezone_offset: str) -> datetime:
    """Convert a UTC datetime to a local datetime based on a timezone offset.

    Args:
        utc_datetime (datetime): The datetime object in UTC to be converted.
        timezone_offset (str): The timezone offset string in format '+HH:MM' or '-HH:MM'.

    Returns:
        datetime: The converted local datetime object.
    """

    offset_hours, offset_minutes = map(int, timezone_offset.split(":"))
    offset = tzoffset(None, offset_hours * 3600 + offset_minutes * 60)

    return utc_datetime.astimezone(offset)


def pretty_json_dumps(obj: Any) -> str:
    """Convert an object to a JSON string with indentation for better readability.

    This function is a wrapper around json.dumps, and it is specifically designed
    for converting objects containing slack message data to JSON strings. The output
    JSON strings have an indentation level of 4 for readability, and it does not
    ensure ASCII encoding to maintain non-Latin characters in the original form.

    Args:
        obj (Any): The Python object to be converted into a JSON string. This is
            typically a dictionary containing slack message data and other related
            metadata.

    Returns:
        str: A JSON string representing the input object.
    """

    return json.dumps(obj, indent=JSON_INDENT_LEVEL, ensure_ascii=False)


def subtract_documents(documents: List[Document], previous_documents: List[Document]) -> List[Document]:
    """Subtracts two lists of documents.

    This method will return a list of documents from the `documents` that are not present in the `previous_documents`.

    Args:
        documents (List[Document]): A list of current documents.
        previous_documents (List[Document]): A list of previous documents.

    Returns:
        List[Document]: A list of documents that are present in the `documents` but not in the `previous_documents`.
    """

    return [doc for doc in documents if doc not in previous_documents]
