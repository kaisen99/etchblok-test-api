---
title: Collection Architecture
description: An explanation of the differences between manual bookmark groups and rule-based smart collections.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067]
section_id: b59d7c89-5b3f-4dcd-bd00-6e210a90eaf5_collection_architecture
doc_type: explanation
section_type: guide
---
The collection architecture in this project provides two distinct ways to group bookmarks: **Manual Collections** and **Smart Collections**. This design allows for both explicit user curation and automated, rule-based organization within the same structural framework.

### The Collection Model
At the core of this architecture is the `Collection` dataclass defined in `app/models/collection.py`. It uses the `CollectionType` enum to distinguish between the two behaviors:

```python
class CollectionType(Enum):
    """The kind of collection."""
    MANUAL = "manual"
    SMART = "smart"
```

The `Collection` model maintains an ordered list of `bookmark_ids`. While both types share this attribute, the way this list is populated differs fundamentally between them.

### Manual Collections
Manual collections are the standard user-curated groups. They are characterized by explicit membership management. The `BookmarkService` provides methods like `add_to_collection` and `remove_from_collection` which delegate to the model's internal logic.

In `app/models/collection.py`, the `add_bookmark` method enforces the manual nature of these collections:

```python
def add_bookmark(self, bookmark_id: str) -> bool:
    """Add a bookmark to a manual collection.

    Returns:
        True if added, False if already present or collection is smart.
    """
    if self.is_smart or bookmark_id in self.bookmark_ids:
        return False
    self.bookmark_ids.append(bookmark_id)
    return True
```

This implementation ensures that users cannot manually inject bookmarks into a collection designated as "smart," maintaining the integrity of the rule-based system.

### Smart Collections and Filter Rules
Smart collections are designed to auto-populate based on a `filter_rule`. This rule is a string that the system uses to match against bookmark attributes. The `Collection` model includes a `_apply_filter` method that demonstrates the intended logic:

```python
def _apply_filter(self, bookmarks: list) -> List[str]:
    """Evaluate the filter_rule against a list of bookmarks.

    Internal method used by the service layer to populate smart collections.
    """
    if not self.filter_rule:
        return []
    keyword = self.filter_rule.lower()
    return [b.id for b in bookmarks if keyword in b.title.lower() or keyword in b.description.lower()]
```

Currently, the implementation of smart collections is partially complete. While the `filter_rule` can be set during creation via `app/routes/collections.py`, the `_apply_filter` method is not yet integrated into the standard retrieval flow in `BookmarkService`. This means that while the infrastructure for smart collections exists, they do not yet dynamically update their `bookmark_ids` in the current version of the service layer.

### Service Layer Orchestration
The `BookmarkService` in `app/services/bookmark_service.py` acts as the orchestrator between the API routes and the persistence layer (`BookmarkRepository`). It handles the validation and state transitions for collections.

When a collection is created, the service uses the `from_dict` factory method:

```python
def create_collection(self, data: Dict[str, Any]) -> Tuple[Optional[Collection], Optional[str]]:
    """Create a new collection."""
    name = data.get("name", "").strip()
    if not name:
        return None, "Collection name is required"
    collection = Collection.from_dict(data)
    self._repo.save_collection(collection)
    return collection, None
```

### Design Tradeoffs and Constraints
The architecture imposes several strict constraints to ensure data consistency:

1.  **Immutability of Smart Collections**: As seen in `add_bookmark`, smart collections are read-only from the perspective of manual additions. This prevents "polluting" a rule-based list with manual entries.
2.  **Strict Reordering**: The `reorder` method in the `Collection` model requires that the new list of IDs exactly matches the existing set. This prevents accidental deletion or addition of bookmarks during a simple reordering operation:
    ```python
    def reorder(self, bookmark_ids: List[str]) -> None:
        if set(bookmark_ids) != set(self.bookmark_ids):
            raise ValueError("Reorder list must contain exactly the same bookmark IDs")
        self.bookmark_ids = bookmark_ids
    ```
3.  **Decoupled Filtering**: By placing the filtering logic (`_apply_filter`) inside the model but orchestrating it through the service, the design allows for future expansion (e.g., more complex query languages in `filter_rule`) without changing the underlying storage schema.