"""Internal LRU cache implementation.

This module is internal to the services package. External code should
interact with caching through ``BookmarkService`` which manages
invalidation automatically.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import TypeVar, Generic, Optional, Dict

T = TypeVar("T")

_DEFAULT_MAX_SIZE = 128
_HIT = "hit"
_MISS = "miss"


class LRUCache(Generic[T]):
    """Least-recently-used cache with a fixed capacity.

    Args:
        max_size: Maximum number of entries before eviction.
    """

    def __init__(self, max_size: int = _DEFAULT_MAX_SIZE) -> None:
        self._max_size = max_size
        self._store: OrderedDict[str, T] = OrderedDict()
        self._stats: Dict[str, int] = {"hits": 0, "misses": 0}

    def get(self, key: str) -> Optional[T]:
        """Retrieve a value by key, returning None on miss.

        Accessing an entry moves it to the most-recently-used position.
        """
        if key in self._store:
            self._store.move_to_end(key)
            self._stats["hits"] += 1
            return self._store[key]
        self._stats["misses"] += 1
        return None

    def put(self, key: str, value: T) -> None:
        """Insert or update an entry."""
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def invalidate(self, key: str) -> bool:
        """Remove a single entry. Returns True if the key existed."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        """Evict all entries and reset stats."""
        self._store.clear()
        self._stats = {"hits": 0, "misses": 0}

    @property
    def size(self) -> int:
        """Current number of entries."""
        return len(self._store)

    @property
    def hit_rate(self) -> float:
        """Ratio of hits to total lookups. Returns 0.0 if no lookups yet."""
        total = self._stats["hits"] + self._stats["misses"]
        return self._stats["hits"] / total if total else 0.0

    def _evict_oldest(self) -> Optional[str]:
        """Remove and return the key of the least-recently-used entry."""
        if self._store:
            key, _ = self._store.popitem(last=False)
            return key
        return None
