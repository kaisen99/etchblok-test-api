"""Tag model for organising bookmarks."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional


class TagColor(Enum):
    """Preset colours available for tags."""

    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    GRAY = "gray"


@dataclass
class Tag:
    """A label that can be attached to one or more bookmarks.

    Attributes:
        id: Unique identifier.
        name: Display name (must be unique per user).
        color: Visual colour for UI rendering.
        description: Optional description of what this tag represents.
        usage_count: Number of bookmarks currently using this tag.
    """

    name: str
    color: TagColor = TagColor.GRAY
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    usage_count: int = 0

    # ── Public methods ──────────────────────────────────────────────

    def rename(self, new_name: str) -> None:
        """Rename the tag.

        Args:
            new_name: The new display name.

        Raises:
            ValueError: If the name is empty or too long.
        """
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Tag name cannot be empty")
        if len(new_name) > 50:
            raise ValueError("Tag name cannot exceed 50 characters")
        self.name = new_name

    def increment_usage(self) -> int:
        """Record that a bookmark now uses this tag. Returns new count."""
        self.usage_count += 1
        return self.usage_count

    def decrement_usage(self) -> int:
        """Record that a bookmark removed this tag. Returns new count."""
        self.usage_count = max(0, self.usage_count - 1)
        return self.usage_count

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a JSON-safe dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color.value,
            "description": self.description,
            "usage_count": self.usage_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        """Construct a Tag from a dictionary."""
        color = TagColor(data["color"]) if "color" in data else TagColor.GRAY
        return cls(name=data["name"], color=color, description=data.get("description", ""))

    # ── Dunder ──────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"Tag(name={self.name!r}, color={self.color.value})"

    def __lt__(self, other: "Tag") -> bool:
        """Allow sorting tags alphabetically by name."""
        return self.name.lower() < other.name.lower()

    # ── Internal ────────────────────────────────────────────────────

    def _normalize_name(self) -> str:
        """Return a lowered, stripped version for uniqueness checks."""
        return self.name.strip().lower()
