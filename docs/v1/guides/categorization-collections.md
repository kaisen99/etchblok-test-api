---
title: Categorization & Collections
description: Advanced organization features including manual grouping, smart collections with filter rules, and tagging systems.
code_symbols: [SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67]
section_id: 9936bc63-73a1-4990-9bef-b065d60c9a2f_categorization___collections
doc_type: how_to
section_type: guide
---
This guide explains how to organize and categorize bookmarks using the tagging and collection systems. These features are managed primarily through the `BookmarkService` and the `Collection` and `Tag` models.

## Organizing with Collections

Collections allow you to group bookmarks. The system supports two types of collections defined in `app/models/collection.py`: **Manual** and **Smart**.

### Creating a Manual Collection
Manual collections require you to explicitly add or remove bookmarks.

```python
from app.services.bookmark_service import BookmarkService
from app.models.collection import CollectionType

service = BookmarkService()

# Create a manual collection
collection_data = {
    "name": "Research Project",
    "type": "manual"
}
collection, error = service.create_collection(collection_data)

# Add a bookmark to the collection
bookmark_id = "abc123def456"
success = service.add_to_collection(collection.id, bookmark_id)
```

### Creating a Smart Collection
Smart collections use a `filter_rule` to automatically identify relevant bookmarks. The filtering logic in `Collection._apply_filter` performs a case-insensitive search for the rule keyword within bookmark titles and descriptions.

```python
# Create a smart collection for Python-related bookmarks
smart_data = {
    "name": "Python Resources",
    "type": "smart",
    "filter_rule": "python"
}
smart_collection, error = service.create_collection(smart_data)
```

### Pinning and Reordering
Collections can be pinned for priority display in the UI. Manual collections also support custom ordering of their bookmarks.

```python
collection = service.get_collection(collection_id)

# Pin the collection
collection.pin()

# Reorder bookmarks (Manual collections only)
# Note: The list must contain exactly the same IDs currently in the collection
new_order = ["id_2", "id_1", "id_3"]
collection.reorder(new_order)
service._repo.save_collection(collection)
```

## Categorizing with Tags

Tags are labels with names and colors that can be attached to multiple bookmarks. They are defined in `app/models/tag.py`.

### Creating and Applying Tags
Tags are created via the `BookmarkService` and can be associated with bookmarks during creation or by updating the bookmark.

```python
from app.models.tag import TagColor

# Create a new tag
tag_data = {
    "name": "Urgent",
    "color": "red",
    "description": "Items requiring immediate attention"
}
tag, error = service.create_tag(tag_data)

# Create a bookmark with the tag
bookmark_data = {
    "url": "https://example.com",
    "title": "Critical Update",
    "tags": [tag.id]
}
bookmark, error = service.create_bookmark(bookmark_data)
```

### Managing Tag Lifecycle
The `BookmarkService` ensures data integrity when tags are modified or deleted. When a tag is deleted via `delete_tag`, the service automatically removes that tag ID from all associated bookmarks and invalidates their cache.

```python
# Update a tag's appearance
service.update_tag(tag.id, {"color": "purple", "name": "High Priority"})

# Delete a tag (automatically cleans up bookmark references)
service.delete_tag(tag.id)
```

## API Integration

The organization features are exposed via REST endpoints in `app/routes/collections.py` and `app/routes/tags.py`.

| Task | Method | Endpoint |
| :--- | :--- | :--- |
| Create Collection | `POST` | `/api/collections/` |
| Add to Collection | `PUT` | `/api/collections/<id>/bookmarks` |
| List Tags | `GET` | `/api/tags/` |
| Delete Tag | `DELETE` | `/api/tags/<id>` |

### Example: Adding a Bookmark to a Collection via API
```bash
curl -X PUT http://localhost:5000/api/collections/coll_123/bookmarks \
     -H "Content-Type: application/json" \
     -d '{"bookmark_id": "book_456"}'
```

## Troubleshooting & Constraints

- **Smart Collection Limitations**: You cannot manually add bookmarks to a smart collection. The `add_bookmark` method in the `Collection` model will return `False` if the `collection_type` is `SMART`.
- **Reordering Errors**: The `reorder` method raises a `ValueError` if the provided list of IDs does not match the set of IDs already in the collection. You cannot use `reorder` to add or remove bookmarks.
- **Reserved Tag Names**: Certain names like "all", "untagged", "archived", and "trash" are reserved and cannot be used for custom tags (enforced in `app/models/_validators.py`).
- **Tag Name Length**: Tag names are limited to 50 characters. Names longer than this will trigger a validation error during creation or renaming.
