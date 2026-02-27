"""Internal validation helpers.

This module is NOT part of the public API. All functions are prefixed
with underscore or are module-private.
"""
import re
from typing import Optional

_URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

_MAX_TITLE_LENGTH = 256
_MAX_DESCRIPTION_LENGTH = 2048
_RESERVED_TAG_NAMES = frozenset({"all", "untagged", "archived", "trash"})


def _validate_url(url: str) -> Optional[str]:
    """Return an error message if *url* is invalid, else None."""
    if not url or not _URL_PATTERN.match(url):
        return "Invalid URL format"
    return None


def _validate_title(title: str) -> Optional[str]:
    """Return an error message if *title* is invalid, else None."""
    if not title or not title.strip():
        return "Title is required"
    if len(title) > _MAX_TITLE_LENGTH:
        return f"Title must be {_MAX_TITLE_LENGTH} characters or fewer"
    return None


def _validate_description(desc: str) -> Optional[str]:
    """Return an error if *desc* exceeds length limit."""
    if len(desc) > _MAX_DESCRIPTION_LENGTH:
        return f"Description must be {_MAX_DESCRIPTION_LENGTH} characters or fewer"
    return None


def _validate_tag_name(name: str) -> Optional[str]:
    """Return an error if the tag name is reserved or too short."""
    normalized = name.strip().lower()
    if not normalized:
        return "Tag name is required"
    if normalized in _RESERVED_TAG_NAMES:
        return f"'{name}' is a reserved tag name"
    if len(normalized) > 50:
        return "Tag name must be 50 characters or fewer"
    return None


def _sanitize_html(text: str) -> str:
    """Strip basic HTML tags from text. Very naive implementation."""
    return re.sub(r"<[^>]+>", "", text)
