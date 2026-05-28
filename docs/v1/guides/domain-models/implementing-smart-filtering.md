---
title: Implementing Smart Filtering
description: A deep dive into the design of smart collections and how filter rules are evaluated against bookmark content.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#664bcdae74f24d832fff86d384111517f11be0db, SYM#67d634120bee630945450829e511171fd936cf36]
section_id: 8571e87a-7ec7-46e8-80c5-6db916c9512d_implementing_smart_filtering
doc_type: explanation
section_type: guide
---
In this project, collections serve as the primary organizational tool for bookmarks. The implementation distinguishes between static, user-managed groups and dynamic, rule-based groups through the `CollectionType` enumeration. This design allows the system to support both explicit curation and automated categorization within the same unified `Collection` model.

## Collection Types and Behavior

The `Collection` class (found in `app/models/collection.py`) uses the `CollectionType` enum to determine how its `bookmark_ids` list is populated and maintained.

*   **Manual Collections (`CollectionType.MANUAL`)**: These function as standard folders. Users explicitly add or remove bookmarks using the `add_bookmark` and `remove_bookmark` methods.
*   **Smart Collections (`CollectionType.SMART`)**: These function as "saved searches." Instead of manual management, they rely on a `filter_rule` to determine membership.

The distinction is enforced at the model level. For instance, the `add_bookmark` method contains a guard clause that prevents manual modification of smart collections:

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

## The Filtering Mechanism

Smart filtering is implemented via the `_apply_filter` method. This method encapsulates the logic for evaluating whether a set of bookmarks meets the criteria defined by the collection's `filter_rule`.

### Evaluation Logic
The current implementation uses a simple but effective substring matching strategy. It evaluates the `filter_rule` against two specific fields of the `Bookmark` model: `title` and `description`.

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

Key characteristics of this implementation include:
1.  **Case-Insensitivity**: Both the keyword and the bookmark content are normalized to lowercase before comparison, ensuring that a rule like "Python" matches "python", "PYTHON", and "Pythonic".
2.  **OR Logic**: A bookmark is included if the keyword appears in *either* the title or the description.
3.  **ID Projection**: The method returns a list of bookmark IDs rather than full objects, maintaining consistency with the `bookmark_ids` attribute of the `Collection` class.

## Design Tradeoffs and Constraints

### Internal Evaluation
The `_apply_filter` method is prefixed with an underscore, signaling that it is intended for internal use by the service layer. In the current architecture, the `BookmarkService` handles the creation of these collections via `create_collection`, but the actual "live" evaluation—where the `bookmark_ids` list is updated in real-time as new bookmarks are added to the system—is a separate responsibility from the model itself.

### Simple vs. Complex Queries
The project currently opts for a single-string keyword match. While this limits the complexity of filters (e.g., no boolean operators like `AND` or `NOT`), it provides a predictable and performant way to implement basic smart folders without the overhead of a complex query parser.

### Manual Override Restriction
By returning `False` in `add_bookmark` when `is_smart` is true, the system maintains strict data integrity for smart collections. This prevents a "hybrid" state where a collection contains both automatically filtered items and manually added ones, which would complicate the logic for refreshing the collection's contents.

## API Integration

Users can create smart collections by providing the `type` and `filter_rule` fields to the `/collections/` endpoint. The `Collection.from_dict` method handles the translation from the API request to the internal model:

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Collection":
    """Construct from a dictionary."""
    ctype = CollectionType(data.get("type", "manual"))
    return cls(
        name=data["name"],
        collection_type=ctype,
        filter_rule=data.get("filter_rule", ""),
    )
```

When a smart collection is created this way, the `filter_rule` is stored as a persistent attribute, allowing the system to re-evaluate the collection's membership whenever the underlying bookmark data changes.
