---
title: Creating and Updating Tags
description: A practical guide to programmatically managing tags using the BookmarkService.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1]
section_id: 9e7b508b-2d68-4d03-a85d-87ac939933a1_creating_and_updating_tags
doc_type: how_to
section_type: guide
---
To manage tags in this project, use the `BookmarkService` class. It provides a high-level interface for creating, updating, and deleting tags while ensuring data consistency across bookmarks.

## Creating a Tag

You create a tag by passing a dictionary of attributes to `BookmarkService.create_tag`. The service validates the tag name and handles persistence.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

tag_data = {
    "name": "Research",
    "color": "blue",
    "description": "Academic and work-related research"
}

tag, error = service.create_tag(tag_data)

if error:
    print(f"Failed to create tag: {error}")
else:
    print(f"Created tag '{tag.name}' with ID: {tag.id}")
```

### Validation Rules
The `create_tag` method uses `_validate_tag_name` (from `app.models._validators`) which enforces the following:
- **Reserved Names**: You cannot use `all`, `untagged`, `archived`, or `trash` as tag names.
- **Length**: Tag names must be 50 characters or fewer.
- **Uniqueness**: While the service doesn't explicitly check for uniqueness in `create_tag`, the underlying repository typically enforces it based on the normalized name (stripped and lowercased).

## Updating a Tag

Use `BookmarkService.update_tag` to modify an existing tag's name or color. This method supports partial updates; you only need to provide the fields you wish to change.

```python
tag_id = "a1b2c3d4"
update_data = {
    "name": "Deep Research",
    "color": "purple"
}

updated_tag, error = service.update_tag(tag_id, update_data)

if updated_tag:
    print(f"Updated tag name to: {updated_tag.name}")
```

### Tag Colors
The `color` field must be one of the values defined in the `TagColor` enum (found in `app.models.tag`):
- `red`
- `blue`
- `green`
- `yellow`
- `purple`
- `gray` (Default)

If you provide an invalid color string, the service will raise a `ValueError` when attempting to cast it to the `TagColor` enum.

## Deleting a Tag

Deleting a tag via `BookmarkService.delete_tag` performs a cascade cleanup. It removes the tag ID from all bookmarks that were using it and invalidates their cache entries before deleting the tag itself.

```python
tag_id = "a1b2c3d4"
success = service.delete_tag(tag_id)

if success:
    print("Tag deleted and removed from all associated bookmarks.")
else:
    print("Tag not found.")
```

## Associating Tags with Bookmarks

Tags are associated with bookmarks by storing the tag's `id` in the bookmark's `tags` list. You can manage these associations using the `Bookmark` model's methods, then saving the bookmark via the service.

```python
# 1. Retrieve the bookmark
bookmark = service.get_bookmark("bookmark_123")

# 2. Add the tag ID
if bookmark.add_tag("research_tag_id"):
    # 3. Persist the change via the service to handle indexing and caching
    service.update_bookmark(bookmark.id, {"tags": bookmark.tags})
```

### Tracking Usage
The `Tag` model includes a `usage_count` attribute. This is incremented or decremented by the repository or service logic when bookmarks are associated or disassociated with the tag, allowing you to see how many bookmarks use a specific tag.

## Troubleshooting

### Reserved Name Error
If you attempt to create a tag named "trash", `create_tag` will return an error message:
`'trash' is a reserved tag name`. 
Always check the `error` return value from service methods.

### Invalid Color
If you pass an arbitrary string like `"crimson"` to `update_tag`, the application will raise:
`ValueError: 'crimson' is not a valid TagColor`.
Ensure your UI or programmatic inputs match the keys in `TagColor`.

### Tag Not Found
If `update_tag` or `delete_tag` is called with an ID that does not exist in the repository, they will return `(None, None)` or `False` respectively, without raising an exception.