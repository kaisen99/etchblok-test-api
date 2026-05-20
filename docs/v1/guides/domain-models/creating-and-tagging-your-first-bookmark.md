---
title: Creating and Tagging your first Bookmark
description: A step-by-step tutorial on instantiating a Bookmark, creating a Tag, and linking them together.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1]
section_id: 8a89e7b6-c1d7-4451-aa8f-711072989033_creating_and_tagging_your_first_bookmark
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to use the core domain models of the Etchblok API to create a bookmark, define a custom tag, and link them together. By the end, you will have a fully initialized bookmark with metadata and associated tags, ready for serialization.

### Prerequisites

To follow this tutorial, ensure you have the following modules available in your environment:
- `app.models.bookmark`: Contains the `Bookmark` class and `BookmarkStatus` enum.
- `app.models.tag`: Contains the `Tag` class and `TagColor` enum.

### Step 1: Instantiate a Bookmark

First, you need to create a `Bookmark` instance. The `Bookmark` class requires a `url` and a `title`.

```python
from app.models.bookmark import Bookmark

# Create a new bookmark
bookmark = Bookmark(
    url="https://github.com/features/actions",
    title="GitHub Actions Documentation",
    description="Automate, customize, and execute your software development workflows."
)

print(f"Created Bookmark: {bookmark.title} (ID: {bookmark.id})")
```

When you instantiate a `Bookmark`, the system automatically generates a unique 12-character hex ID (e.g., `a1b2c3d4e5f6`) and sets the `created_at` and `updated_at` timestamps to the current UTC time. The default status is `BookmarkStatus.ACTIVE`.

### Step 2: Create a Tag

Next, create a `Tag` to categorize your bookmark. You can specify a name and a color from the `TagColor` enum.

```python
from app.models.tag import Tag, TagColor

# Create a 'DevOps' tag with a blue color
devops_tag = Tag(
    name="DevOps",
    color=TagColor.BLUE,
    description="Tools and practices for automation"
)

print(f"Created Tag: {devops_tag.name} (ID: {devops_tag.id})")
```

Similar to bookmarks, tags generate their own unique 8-character hex ID upon instantiation. The `usage_count` defaults to `0`.

### Step 3: Link the Tag to the Bookmark

To associate the tag with the bookmark, you use the `add_tag` method. This method accepts the `id` of the tag.

```python
# Link the tag to the bookmark
success = bookmark.add_tag(devops_tag.id)

if success:
    # Increment the usage count on the tag model
    devops_tag.increment_usage()
    print(f"Tag '{devops_tag.name}' added to '{bookmark.title}'")
    print(f"New usage count: {devops_tag.usage_count}")
```

The `bookmark.add_tag()` method returns `True` if the tag was successfully added and `False` if the tag ID was already present in the `bookmark.tags` list. Note that calling `add_tag` automatically triggers the internal `_touch()` method, which updates the bookmark's `updated_at` timestamp.

### Step 4: Manage Bookmark State

If you want to organize your bookmarks further, you can move them to the archive or the trash using the built-in state management methods.

```python
from app.models.bookmark import BookmarkStatus

# Archive the bookmark
bookmark.archive()

print(f"Bookmark status: {bookmark.status}") # BookmarkStatus.ARCHIVED
```

The `archive()`, `trash()`, and `restore()` methods update the `status` attribute and refresh the `updated_at` timestamp.

### Step 5: Serialize for API Response

Finally, you can convert your models into plain dictionaries. This is useful for returning data in JSON format from an API endpoint.

```python
# Serialize the bookmark
bookmark_data = bookmark.to_dict()

# Serialize the tag
tag_data = devops_tag.to_dict()

print("Serialized Bookmark Data:")
print(bookmark_data)
```

The `to_dict()` method ensures that enums (like `BookmarkStatus` and `TagColor`) are converted to their string values and `datetime` objects are converted to ISO-formatted strings.

### Important Considerations

When working with these models, keep the following constraints in mind:

*   **Reserved Tag Names**: While the `Tag` model allows any name, the service layer typically prevents using reserved names like `all`, `untagged`, `archived`, and `trash`.
*   **Tag Name Length**: The `tag.rename()` method enforces a maximum length of 50 characters.
*   **ID Uniqueness**: Bookmark IDs (12 chars) and Tag IDs (8 chars) are generated using `uuid4`. While collisions are statistically improbable, the models do not check for global uniqueness; that is handled by the database repository.
*   **Manual Usage Tracking**: The `Bookmark` model does not automatically update the `Tag.usage_count`. You must manually call `tag.increment_usage()` or `tag.decrement_usage()` when modifying associations.