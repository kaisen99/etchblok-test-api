"""Collection model for grouping bookmarks."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any


class CollectionType(Enum):
    """The kind of collection."""

    MANUAL = "manual"
    SMART = "smart"


@dataclass
class Collection:
    """A named group of bookmarks.

    Collections can be **manual** (user adds bookmarks explicitly) or
    **smart** (bookmarks are included automatically based on a filter rule).

    Attributes:
        id: Unique identifier.
        name: Display name.
        collection_type: Whether the collection is manual or smart.
        bookmark_ids: Ordered list of bookmark IDs in the collection.
        filter_rule: For smart collections, a query string that selects bookmarks.
        is_pinned: Whether the collection appears at the top of the sidebar.
        created_at: Creation timestamp.
    """

    name: str
    collection_type: CollectionType = CollectionType.MANUAL
    bookmark_ids: List[str] = field(default_factory=list)
    filter_rule: str = ""
    is_pinned: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])
    created_at: datetime = field(default_factory=datetime.utcnow)

    # ── Public API ──────────────────────────────────────────────────

    @property
    def size(self) -> int:
        """Number of bookmarks in the collection."""
        return len(self.bookmark_ids)

    @property
    def is_smart(self) -> bool:
        """Whether this collection auto-populates based on a filter rule."""
        return self.collection_type == CollectionType.SMART

    def add_bookmark(self, bookmark_id: str) -> bool:
        """Add a bookmark to a manual collection.

        Args:
            bookmark_id: ID of the bookmark to add.

        Returns:
            True if added, False if already present or collection is smart.
        """
        if self.is_smart or bookmark_id in self.bookmark_ids:
            return False
        self.bookmark_ids.append(bookmark_id)
        return True

    def remove_bookmark(self, bookmark_id: str) -> bool:
        """Remove a bookmark from the collection."""
        if bookmark_id not in self.bookmark_ids:
            return False
        self.bookmark_ids.remove(bookmark_id)
        return True

    def reorder(self, bookmark_ids: List[str]) -> None:
        """Replace the bookmark ordering.

        Args:
            bookmark_ids: New ordered list. Must contain the same IDs.

        Raises:
            ValueError: If the provided list doesn't match existing bookmarks.
        """
        if set(bookmark_ids) != set(self.bookmark_ids):
            raise ValueError("Reorder list must contain exactly the same bookmark IDs")
        self.bookmark_ids = bookmark_ids

    def pin(self) -> None:
        """Pin the collection to the top of the sidebar."""
        self.is_pinned = True

    def unpin(self) -> None:
        """Unpin the collection."""
        self.is_pinned = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to JSON-safe dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.collection_type.value,
            "bookmark_ids": self.bookmark_ids,
            "filter_rule": self.filter_rule,
            "is_pinned": self.is_pinned,
            "size": self.size,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Collection":
        """Construct from a dictionary."""
        ctype = CollectionType(data.get("type", "manual"))
        return cls(
            name=data["name"],
            collection_type=ctype,
            filter_rule=data.get("filter_rule", ""),
        )

    # ── Dunder ──────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"Collection(name={self.name!r}, size={self.size})"

    def __contains__(self, bookmark_id: str) -> bool:
        return bookmark_id in self.bookmark_ids

    # ── Internal ────────────────────────────────────────────────────

    def _apply_filter(self, bookmarks: list) -> List[str]:
        """Evaluate the filter_rule against a list of bookmarks.

        Internal method used by the service layer to populate smart collections.
        """
        if not self.filter_rule:
            return []
        keyword = self.filter_rule.lower()
        return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
