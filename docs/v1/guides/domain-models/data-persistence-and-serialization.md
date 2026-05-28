---
title: Data Persistence and Serialization
description: How to convert domain models to and from dictionary formats for JSON API responses and database storage.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: edb8aa61-1692-49fd-8ed2-18b90ac41f08_data_persistence_and_serialization
doc_type: how_to
section_type: guide
---
This guide demonstrates how to convert domain models to and from dictionary formats for JSON API responses and how to persist these models using the repository pattern.

## Serializing Models for API Responses

To convert a domain model into a JSON-serializable dictionary, use the `to_dict()` method. This method handles the conversion of internal types like Enums and datetimes into standard strings.

```python
from flask import jsonify
from app.models.bookmark import Bookmark

def get_bookmark_response(bookmark_id: str):
    # Retrieve the model from the repository
    bookmark = repo.get_bookmark(bookmark_id)
    
    if bookmark:
        # Convert to dictionary for the JSON response
        return jsonify(bookmark.to_dict()), 200
    return jsonify({"error": "Not found"}), 404
```

The `to_dict()` method ensures that:
- **Timestamps**: `created_at` and `updated_at` are converted to ISO 8601 strings using `.isoformat()`.
- **Enums**: Statuses (like `BookmarkStatus`) and colors (like `TagColor`) are converted to their underlying string or integer values.
- **Calculated Fields**: The `Collection` model includes a `size` field in its dictionary representation, which is derived from the length of `bookmark_ids`.

## Creating Models from Request Data

To instantiate a model from a dictionary (such as a JSON request body), use the `from_dict()` class method. This is typically performed in the service layer before persistence.

```python
from app.models.bookmark import Bookmark
from app.services.bookmark_service import BookmarkService

# Example request data
data = {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "A site for examples",
    "tags": ["work", "research"]
}

# Instantiate the model
bookmark = Bookmark.from_dict(data)

# The model generates its own ID and timestamps upon instantiation
print(f"Created Bookmark {bookmark.id} at {bookmark.created_at}")
```

### Model-Specific Deserialization Logic

Each model handles its own dictionary mapping:

*   **Bookmark**: Extracts `url`, `title`, `description`, and `tags`. It ignores `id` and `status` in the input dictionary, generating a new ID and defaulting to `BookmarkStatus.ACTIVE`.
*   **Tag**: Extracts `name`, `color`, and `description`. It maps the `color` string back to a `TagColor` enum.
*   **Collection**: Extracts `name`, `type` (mapped to `CollectionType`), and `filter_rule`.

## Persisting Models in the Repository

Once a model is instantiated or modified, it is persisted using the `BookmarkRepository`. The repository stores the actual model instances, maintaining their state in memory.

```python
from app.models.bookmark import Bookmark
from app.db.repository import BookmarkRepository

repo = BookmarkRepository()

# Create and save
new_bookmark = Bookmark(url="https://github.com", title="GitHub")
repo.save_bookmark(new_bookmark)

# Update and save
bookmark = repo.get_bookmark(new_bookmark.id)
bookmark.archive()  # Changes status and updates updated_at
repo.save_bookmark(bookmark)
```

## Handling Updates and State Changes

When modifying existing data, use the model's public API to ensure internal state (like timestamps) is updated correctly before re-saving to the repository.

```python
from app.models.tag import Tag

def update_tag_name(tag_id: str, new_name: str):
    tag = repo.get_tag(tag_id)
    if tag:
        # Tag.rename includes validation for length and empty strings
        tag.rename(new_name)
        repo.save_tag(tag)
```

### Troubleshooting and Gotchas

*   **Partial Deserialization**: `Bookmark.from_dict` and `Collection.from_dict` are designed for **creation**. They do not accept an `id` or `created_at` from the dictionary; these are always generated fresh by the `dataclass` field factories. To "hydrate" an existing object from a database, you must use the constructor directly or implement a separate hydration method.
*   **Reordering Collections**: When using `Collection.reorder(bookmark_ids)`, the provided list must contain the exact same set of IDs already in the collection. If there is a mismatch, it will raise a `ValueError`.
*   **Tag Validation**: `Tag.rename()` will raise a `ValueError` if the name is empty or exceeds 50 characters. Always wrap these calls in try-except blocks when processing user input.
*   **Private Timestamps**: The `updated_at` field is updated via the `_touch()` method. This is called automatically by state-changing methods like `archive()`, `trash()`, `add_tag()`, and `remove_tag()`. Do not attempt to update `updated_at` manually.
