---
title: Manual and Smart Collections
description: Discusses the design of Collections, contrasting user-curated lists with dynamic smart collections based on filter rules.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db, SYM#67d634120bee630945450829e511171fd936cf36]
section_id: af380269-9efb-42d1-be14-6a51871289e7_manual_and_smart_collections
doc_type: explanation
section_type: guide
---
The **kaisen99-etchblok-test-api-851c354** codebase implements a dual-mode organization system for bookmarks through the `Collection` class. This design allows users to choose between static, hand-curated lists and dynamic, rule-based groupings. By centralizing both behaviors within a single model, the system maintains a consistent interface for the UI while varying the underlying logic for membership.

## The Collection Model

The core of this system is the `Collection` class found in `app/models/collection.py`. It uses the `CollectionType` enum to distinguish between the two modes:

```python
class CollectionType(Enum):
    """The kind of collection."""
    MANUAL = "manual"
    SMART = "smart"
```

Every `Collection` instance tracks its identity (`id`), display name (`name`), and its membership via `bookmark_ids`. However, how those IDs are managed depends entirely on the `collection_type`.

## Manual Collections: Explicit Curation

Manual collections are the standard "folder" or "playlist" equivalent. They rely on explicit user actions to add or remove bookmarks. The implementation enforces this through the `add_bookmark` method:

```python
def add_bookmark(self, bookmark_id: str) -> bool:
    """Add a bookmark to a manual collection."""
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True
```

### Ordering and Integrity
A key feature of manual collections is the ability to define a specific order for bookmarks. The `reorder` method allows the UI to update the sequence of IDs. To prevent accidental data loss, the method includes a strict integrity check:

```python
def reorder(self, bookmark_ids: List[str]) -> None:
    """Replace the bookmark ordering."""
    if set(bookmark_ids) != set(self.bookmark_ids):
        raise ValueError("Reorder list must contain exactly the same bookmark IDs")
    self.bookmark_ids = bookmark_ids
```

This design choice ensures that a reorder operation cannot be used to sneakily add or remove bookmarks; it only permits changing the sequence of the existing set.

## Smart Collections: Rule-Based Filtering

Smart collections are designed to be dynamic. Instead of a static list of IDs, they are defined by a `filter_rule`. The `Collection` model includes an internal method, `_apply_filter`, which demonstrates the intended logic for these collections:

```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks."""
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

In this implementation, smart collections function as saved searches. They scan the `title` and `description` of all bookmarks for a specific keyword. 

### Design Tradeoffs and Current State
There is a notable architectural tradeoff in the current implementation: **smart collections are not yet fully automated**. 

1.  **Orphaned Logic**: While `_apply_filter` exists in the model, it is not currently invoked by the `BookmarkService` or the `BookmarkRepository` during retrieval. This means that a smart collection's `bookmark_ids` list does not automatically refresh when new bookmarks are created.
2.  **Immutable Membership**: The `add_bookmark` method explicitly returns `False` if the collection is smart. This preserves the conceptual integrity of a smart collection—it should only contain what the filter dictates—but since the filter isn't automatically running, smart collections remain empty unless manually initialized.
3.  **Selective Serialization**: The `from_dict` method used during creation (via `BookmarkService.create_collection`) only restores the `name`, `type`, and `filter_rule`. It does not restore `bookmark_ids` or the `is_pinned` status, reinforcing the idea that these attributes are either transient or managed separately from the initial creation payload.

## Service Layer Integration

The `BookmarkService` in `app/services/bookmark_service.py` acts as the coordinator for these models. It handles the persistence of collection state to the `BookmarkRepository`.

```python
def add_to_collection(self, collection_id: str, bookmark_id: str) -> bool:
    """Add a bookmark to a collection."""
    collection = self._repo.get_collection(collection_id)
    if not collection:
        return False
    if not collection.add_bookmark(bookmark_id):
        return False
    self._repo.save_collection(collection)
    return True
```

This service-level logic respects the model's constraints: if a developer attempts to add a bookmark to a smart collection via the API, the `collection.add_bookmark` call will fail, and the service will return `False`, which the API layer (in `app/routes/collections.py`) then translates into a `400 Bad Request`. This ensures that the distinction between manual and smart collections is enforced from the model all the way up to the HTTP interface.