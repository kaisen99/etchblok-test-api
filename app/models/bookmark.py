"""Bookmark model — the core domain entity."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class BookmarkStatus(Enum):
    """Visibility status of a bookmark."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    TRASHED = "trashed"


@dataclass
class Bookmark:
    """A saved URL with metadata, tags, and full-text content.

    Attributes:
        id: Unique identifier.
        url: The bookmarked URL.
        title: Human-readable title.
        description: Optional longer description.
        tags: List of tag IDs associated with this bookmark.
        status: Current visibility status.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last modification.
        metadata: Arbitrary key/value pairs for extensibility.
    """

    url: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    status: BookmarkStatus = BookmarkStatus.ACTIVE
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ── Public API ──────────────────────────────────────────────────

    def archive(self) -> None:
        """Move the bookmark to the archive."""
        self.status = BookmarkStatus.ARCHIVED
        self._touch()

    def trash(self) -> None:
        """Soft-delete the bookmark by moving it to the trash."""
        self.status = BookmarkStatus.TRASHED
        self._touch()

    def restore(self) -> None:
        """Restore a trashed or archived bookmark to active status."""
        self.status = BookmarkStatus.ACTIVE
        self._touch()

    def add_tag(self, tag_id: str) -> bool:
        """Attach a tag. Returns False if already present."""
        if tag_id in self.tags:
            return False
        self.tags.append(tag_id)
        self._touch()
        return True

    def remove_tag(self, tag_id: str) -> bool:
        """Detach a tag. Returns False if not found."""
        if tag_id not in self.tags:
            return False
        self.tags.remove(tag_id)
        self._touch()
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary for JSON responses."""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bookmark":
        """Construct a Bookmark from a dictionary (e.g. JSON body).

        Args:
            data: Dictionary with bookmark fields.

        Returns:
            A new Bookmark instance.

        Raises:
            KeyError: If required fields are missing.
        """
        return cls(
            url=data["url"],
            title=data["title"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )

    # ── Dunder methods ──────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"Bookmark(id={self.id!r}, title={self.title!r}, status={self.status.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bookmark):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # ── Private helpers ─────────────────────────────────────────────

    def _touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = datetime.utcnow()

    def __validate_url(self) -> bool:
        """Name-mangled validation — truly private to the class."""
        return self.url.startswith("http://") or self.url.startswith("https://")
