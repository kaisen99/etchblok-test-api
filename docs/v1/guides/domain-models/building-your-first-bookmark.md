---
title: Building Your First Bookmark
description: A beginner-friendly walkthrough of creating a bookmark, assigning it to a collection, and applying tags.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#e15c91e9e7eae95d052f50388a60d0bc30b3fe67, SYM#97d8a6cbf0c47108aa2beb39fafa695229654067, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b, SYM#a903c58b7b9829413e7dde33ff94fc7516b965f1, SYM#664bcdae74f24d832fff86d384111517f11be0db]
section_id: b62c92d6-d3ae-4958-b1c5-48c99282c341_building_your_first_bookmark
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to use the core models of the **kaisen99-etchblok-test-api-e41805c** codebase to create a bookmark, organize it with tags, and group it into collections.

By the end of this guide, you will have a fully initialized bookmark linked to a custom tag and stored within both a manual and a smart collection.

### Prerequisites

To follow this tutorial, ensure you have the following classes available in your environment:
- `Bookmark` and `BookmarkStatus` from `app.models.bookmark`
- `Tag` and `TagColor` from `app.models.tag`
- `Collection` and `CollectionType` from `app.models.collection`

### Step 1: Create a New Bookmark

The foundation of the system is the `Bookmark` class. You can create one by providing a URL and a title.

```python
from app.models.bookmark import Bookmark, BookmarkStatus

# Initialize a new bookmark
bookmark = Bookmark(
    url="https://github.com/features/actions",
    title="GitHub Actions Documentation",
    description="Learn how to automate your workflow with GitHub Actions."
)

print(f"Created Bookmark: {bookmark.title} (ID: {bookmark.id})")
print(f"Status: {bookmark.status.value}")
```

When you instantiate a `Bookmark`, the system automatically generates a 12-character unique ID and sets the status to `BookmarkStatus.ACTIVE`.

### Step 2: Create and Apply a Tag

Tags allow you to categorize bookmarks across different collections. You create a `Tag` independently and then associate its ID with the bookmark.

```python
from app.models.tag import Tag, TagColor

# Create a tag for 'DevOps'
devops_tag = Tag(
    name="DevOps",
    color=TagColor.BLUE,
    description="Tools and practices for software delivery"
)

# Associate the tag with the bookmark
added = bookmark.add_tag(devops_tag.id)

if added:
    devops_tag.increment_usage()
    print(f"Tag '{devops_tag.name}' applied to bookmark.")
    print(f"Tag usage count: {devops_tag.usage_count}")
```

The `add_tag` method ensures that duplicate tags aren't added to the same bookmark. Note that you must manually call `increment_usage()` on the `Tag` instance to keep the usage statistics accurate if you are working directly with the models.

### Step 3: Organize into a Manual Collection

Collections are used to group related bookmarks. A `MANUAL` collection requires you to explicitly add bookmark IDs.

```python
from app.models.collection import Collection, CollectionType

# Create a manual collection for work projects
work_collection = Collection(
    name="Work Resources",
    collection_type=CollectionType.MANUAL
)

# Add the bookmark to the collection
success = work_collection.add_bookmark(bookmark.id)

if success:
    print(f"Added to collection: {work_collection.name}")
    print(f"Collection size: {work_collection.size}")
```

The `add_bookmark` method returns `False` if the bookmark is already in the collection or if the collection is a "Smart" collection.

### Step 4: Automate with a Smart Collection

Smart collections use a `filter_rule` to automatically include bookmarks based on their title or description.

```python
# Create a smart collection that looks for 'GitHub'
github_collection = Collection(
    name="GitHub Tools",
    collection_type=CollectionType.SMART,
    filter_rule="GitHub"
)

# Check if our bookmark matches the filter
# (In the real app, the service layer handles this automatically)
matches = github_collection._apply_filter([bookmark])

if bookmark.id in matches:
    print(f"Bookmark '{bookmark.title}' automatically matched the '{github_collection.name}' smart collection.")
```

Smart collections are dynamic. Instead of storing a static list of IDs via `add_bookmark`, they evaluate the `filter_rule` against your library to determine membership.

### Final Result

You have now successfully built a structured bookmark entry. Here is how your data looks when serialized:

```python
import json

# View the final bookmark state
print(json.dumps(bookmark.to_dict(), indent=2))

# View the collection state
print(json.dumps(work_collection.to_dict(), indent=2))
```

### Next Steps
- Explore the `BookmarkService` in `app/services/bookmark_service.py` to see how these models are persisted to a database.
- Learn how to move bookmarks to the trash using `bookmark.trash()`.
- Experiment with pinning important collections using `work_collection.pin()`.
