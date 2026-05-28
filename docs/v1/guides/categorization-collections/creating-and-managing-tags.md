---
title: Creating and Managing Tags
description: Learn how to define labels, assign colors, and manage the lifecycle of tags used for bookmark categorization.
code_symbols: [SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#8d687603253ce34b667ab707a05b20e9357dd6af]
section_id: 9e2705a8-e235-4f83-b40d-1dea576459d5_creating_and_managing_tags
doc_type: how_to
section_type: guide
---
To create and manage tags in this project, you primarily interact with the `BookmarkService` which orchestrates the `Tag` model and the `BookmarkRepository`.

### Creating a New Tag

To create a tag, use the `create_tag` method of the `BookmarkService`. This method handles validation and persistence.

```python
from app.services.bookmark_service import BookmarkService
from app.models.tag import TagColor

service = BookmarkService()

tag_data = {
    "name": "Research",
    "color": TagColor.BLUE.value,
    "description": "Academic and technical papers"
}

tag, error = service.create_tag(tag_data)

if error:
    print(f"Failed to create tag: {error}")
else:
    print(f"Created tag {tag.name} with ID {tag.id}")
```

### Updating Tag Properties

You can update a tag's name or color using `update_tag`. The service ensures that name changes are validated and that the repository is updated.

```python
from app.services.bookmark_service import BookmarkService
from app.models.tag import TagColor

service = BookmarkService()

# Update tag name and color
updates = {
    "name": "Deep Learning",
    "color": TagColor.PURPLE.value
}

updated_tag, error = service.update_tag("a1b2c3d4", updates)
```

The `Tag` model (in `app/models/tag.py`) also provides a `rename()` method for direct manipulation, which includes internal length and content validation:

```python
from app.models.tag import Tag

tag = Tag(name="Old Name")
tag.rename("New Name") # Validates length <= 50 and non-empty
```

### Listing and Sorting Tags

Tags can be retrieved as a list and are naturally sortable by name (case-insensitive) due to the `__lt__` implementation in the `Tag` class.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
tags = service.list_tags()

# Sort tags alphabetically by name
sorted_tags = sorted(tags)

for t in sorted_tags:
    print(f"{t.name} ({t.usage_count} bookmarks)")
```

### Managing Tag Usage Counts

The `Tag` model tracks how many bookmarks are using it via the `usage_count` attribute. While the service layer typically manages this during bookmark updates, you can manually adjust counts using the model's methods:

```python
tag.increment_usage() # Returns new count
tag.decrement_usage() # Returns new count, floors at 0
```

### Deleting Tags and Cascading Changes

When a tag is deleted via `BookmarkService.delete_tag`, the service automatically removes that tag ID from all associated bookmarks and invalidates their cache entries before removing the tag from the repository.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# This removes the tag from the system and all bookmarks using it
success = service.delete_tag("a1b2c3d4")
```

### Validation Rules and Constraints

Tag management is subject to several constraints defined in `app/models/_validators.py`:

*   **Name Length**: Must be between 1 and 50 characters.
*   **Reserved Names**: The following names are reserved and cannot be used for custom tags: `all`, `untagged`, `archived`, `trash`.
*   **Colors**: Must be one of the values defined in `TagColor`: `RED`, `BLUE`, `GREEN`, `YELLOW`, `PURPLE`, or `GRAY` (default).
*   **Unique IDs**: IDs are automatically generated as 8-character hex strings (e.g., `uuid.uuid4().hex[:8]`).

### Troubleshooting: Reserved Names

If you attempt to create or rename a tag to a reserved name, the service will return an error message.

```python
# This will fail validation
tag_data = {"name": "archived"}
tag, error = service.create_tag(tag_data)
# error will be "'archived' is a reserved tag name"
```
