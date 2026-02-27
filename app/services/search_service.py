"""In-memory full-text search index for bookmarks.

Provides a simple inverted index suitable for small datasets.
For production use you'd replace this with Typesense, Elasticsearch, etc.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import List, Dict, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.repository import BookmarkRepository

from app.models.bookmark import Bookmark

# ── Module-level constants ──────────────────────────────────────────
_STOP_WORDS: Set[str] = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "it"}
_TOKEN_RE = re.compile(r"[a-z0-9]+")
MAX_SEARCH_RESULTS = 100


class SearchIndex:
    """Inverted index mapping tokens to bookmark IDs.

    Rebuilt from the repository on initialisation and updated
    incrementally when bookmarks are added or modified.

    Args:
        repository: The bookmark repository to index from.
    """

    def __init__(self, repository: "BookmarkRepository") -> None:
        self._repo = repository
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._rebuild()

    # ── Public API ──────────────────────────────────────────────────

    def index_bookmark(self, bookmark: Bookmark) -> None:
        """Add or update a bookmark in the index.

        Args:
            bookmark: The bookmark to index.
        """
        self._remove_bookmark_from_index(bookmark.id)
        tokens = self._tokenize(f"{bookmark.title} {bookmark.description}")
        for token in tokens:
            self._index[token].add(bookmark.id)

    def remove_bookmark(self, bookmark_id: str) -> None:
        """Remove a bookmark from the index."""
        self._remove_bookmark_from_index(bookmark_id)

    def search(self, query: str, limit: int = 20) -> List[Bookmark]:
        """Search bookmarks matching the query string.

        Tokens are AND-ed together — all must appear for a result to match.

        Args:
            query: Free-text search query.
            limit: Maximum number of results.

        Returns:
            List of matching bookmarks, ordered by relevance (number of token hits).
        """
        tokens = self._tokenize(query)
        if not tokens:
            return []

        candidate_ids: Set[str] = self._index.get(tokens[0], set()).copy()
        for token in tokens[1:]:
            candidate_ids &= self._index.get(token, set())

        results = []
        for bid in candidate_ids:
            bookmark = self._repo.get_bookmark(bid)
            if bookmark:
                results.append(bookmark)

        return self._rank_results(results, tokens)[:limit]

    # ── Private helpers ─────────────────────────────────────────────

    def _rebuild(self) -> None:
        """Rebuild the entire index from the repository."""
        self._index.clear()
        all_bookmarks, _ = self._repo.list_bookmarks(page=1, per_page=10000)
        for bookmark in all_bookmarks:
            self.index_bookmark(bookmark)

    def _tokenize(self, text: str) -> List[str]:
        """Split text into lowercase tokens, removing stop words."""
        tokens = _TOKEN_RE.findall(text.lower())
        return [t for t in tokens if t not in _STOP_WORDS]

    def _remove_bookmark_from_index(self, bookmark_id: str) -> None:
        """Remove all index entries for a bookmark ID."""
        empty_tokens = []
        for token, ids in self._index.items():
            ids.discard(bookmark_id)
            if not ids:
                empty_tokens.append(token)
        for token in empty_tokens:
            del self._index[token]

    @staticmethod
    def _rank_results(bookmarks: List[Bookmark], tokens: List[str]) -> List[Bookmark]:
        """Rank results by number of token occurrences in title + description."""
        def score(b: Bookmark) -> int:
            text = f"{b.title} {b.description}".lower()
            return sum(text.count(t) for t in tokens)

        return sorted(bookmarks, key=score, reverse=True)
