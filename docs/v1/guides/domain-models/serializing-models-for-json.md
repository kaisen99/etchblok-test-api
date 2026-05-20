---
title: Serializing Models for JSON
description: A practical guide on using to_dict and from_dict methods to handle API requests and responses.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: 6723fdb1-a143-4002-a617-cb8d70817d00_serializing_models_for_json
doc_type: how_to
section_type: guide
---
To handle API requests and responses, this project uses a consistent pattern of `to_dict` and `from_dict` methods across its core models. This approach ensures that complex Python types like datetimes and Enums are correctly serialized for JSON responses and that incoming request data is safely converted into model instances.

## Serializing Models for JSON Responses

To return a model as a JSON response in a Flask route, call the `to_dict()` method and pass the result to `flask.jsonify()`.

```python
# app/routes/bookmarks.py

@bookmarks_bp.route("/<bookmark_id>", methods=["GET"])
def get_bookmark(bookmark_id: str):
    bookmark = _service.get_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    
    # Convert the Bookmark instance to a JSON-serializable dictionary
    return jsonify(bookmark.to_dict())
```

### How to_dict Handles Complex Types
The `to_dict` implementation in classes like `Bookmark` and `Collection` performs several transformations to ensure JSON compatibility:

1.  **Dates**: Converts `datetime` objects to ISO 8601 strings using `.isoformat()`.
2.  **Enums**: Exports the underlying string or integer value of an Enum (e.g., `self.status.value`).
3.  **Calculated Properties**: Includes properties that are not stored attributes, such as the `size` of a `Collection`.

```python
# Example output from Bookmark.to_dict()
{
    "id": "a1b2c3d4e5f6",
    "url": "https://example.com",
    "title": "Example",
    "status": "active",  # Enum value
    "created_at": "2023-10-27T10:00:00.000000",  # ISO format
    "metadata": {}
}
```

## Creating Models from Request Data

Use the `@classmethod from_dict` to instantiate models from raw dictionary data, typically received from `request.get_json()`.

```python
# app/services/bookmark_service.py

def create_bookmark(self, data: Dict[str, Any]) -> Tuple[Optional[Bookmark], Optional[str]]:
    # 1. Validate raw data first
    error = _validate_url(data.get("url", "")) or _validate_title(data.get("title", ""))
    if error:
        return None, error

    # 2. Instantiate model using from_dict
    bookmark = Bookmark.from_dict(data)
    
    # 3. Persist the new instance
    self._repo.save_bookmark(bookmark)
    return bookmark, None
```

### Field Mapping in from_dict
The `from_dict` methods are designed for **creation**. They typically only extract fields that a user is allowed to provide, while internal fields like `id`, `created_at`, and `updated_at` are generated automatically by the class's `field(default_factory=...)` definitions.

*   **Bookmark**: Extracts `url`, `title`, `description`, and `tags`.
*   **Tag**: Extracts `name`, `color`, and `description`.
*   **Collection**: Extracts `name`, `type`, and `filter_rule`.

## Handling Enums and Defaults

When deserializing, models must convert raw strings back into Enum types. The `Tag` and `Collection` models demonstrate how to handle this safely.

```python
# app/models/tag.py

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Tag":
    # Convert string color to TagColor enum, defaulting to GRAY if missing
    color = TagColor(data["color"]) if "color" in data else TagColor.GRAY
    return cls(
        name=data["name"], 
        color=color, 
        description=data.get("description", "")
    )
```

In `Collection.from_dict`, a default value is provided directly to the Enum constructor:
```python
# app/models/collection.py

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Collection":
    ctype = CollectionType(data.get("type", "manual"))
    return cls(
        name=data["name"],
        collection_type=ctype,
        filter_rule=data.get("filter_rule", ""),
    )
```

## Troubleshooting and Gotchas

### KeyError on Missing Fields
The `from_dict` methods for `Bookmark` and `Tag` access required fields like `url` or `name` using direct key access (`data["url"]`). If these keys are missing from the input dictionary, a `KeyError` will be raised. 

**Solution**: Always perform validation in the Service layer (e.g., using `_validate_url`) before calling `from_dict`.

### Partial Updates
The `from_dict` method is not suitable for partial updates (PATCH/PUT) because it creates a *new* instance with a new ID. For updates, modify the existing instance attributes directly as seen in `BookmarkService.update_bookmark`:

```python
# Correct pattern for updates in app/services/bookmark_service.py
bookmark = self._repo.get_bookmark(bookmark_id)
if "title" in data:
    bookmark.title = data["title"]
bookmark._touch() # Update the updated_at timestamp
```

### Calculated Fields are Read-Only
Fields like `size` in `Collection.to_dict()` are generated by properties. They are included in the JSON response for the UI but cannot be passed back into `from_dict` to modify the collection.