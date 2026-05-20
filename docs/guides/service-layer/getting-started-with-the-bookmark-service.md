---
title: Getting Started with the Bookmark Service
description: A step-by-step introduction to initializing the BookmarkService and performing your first create and retrieve operations.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1, SYM#fdcfaed9972e477ae4585fd1b279ac107fa534cd]
section_id: 2388af11-260a-4fe5-931d-18b18fa4a5b8_getting_started_with_the_bookmark_service
doc_type: tutorial
---

In this tutorial, you will learn how to use the `BookmarkService` to manage your digital library. You will initialize the service, create your first bookmark with validation, retrieve it using the built-in cache, and perform a full-text search.

The `BookmarkService` acts as a central facade in this application, orchestrating interactions between the database, the search index, and the cache.

### Prerequisites

Before you begin, ensure you have the application environment configured. The service relies on the following internal components which are initialized automatically:
- `BookmarkRepository` for persistence.
- `LRUCache` for performance.
- `SearchIndex` for full-text search capabilities.

### Step 1: Initialize the Bookmark Service

The `BookmarkService` is implemented as a singleton. This ensures that the repository and cache state are shared across your entire application, whether you are accessing it from a Flask blueprint or a background task.

```python
from app.services.bookmark_service import BookmarkService

# Initialize the service
service = BookmarkService()

# Because it is a singleton, subsequent calls return the same instance
another_reference = BookmarkService()
assert service is another_reference
```

### Step 2: Create Your First Bookmark

To create a bookmark, you pass a dictionary of data to the `create_bookmark` method. This method returns a tuple containing the created `Bookmark` object (on success) and an error message (on failure).

```python
bookmark_data = {
    "url": "https://github.com/kaisen99/etchblok",
    "title": "Etchblok Repository",
    "description": "The main repository for the Etchblok project."
}

bookmark, error = service.create_bookmark(bookmark_data)

if error:
    print(f"Failed to create bookmark: {error}")
else:
    print(f"Successfully created bookmark: {bookmark.id}")
    print(f"URL: {bookmark.url}")
```

The service automatically performs validation on the `url` and `title`. If you provide an invalid URL or an empty title, the `bookmark` result will be `None` and the `error` string will contain the validation message.

### Step 3: Retrieve a Bookmark from Cache

Once a bookmark is created or retrieved, the `BookmarkService` stores it in an internal `LRUCache` (with a default capacity of 256 items). This reduces database load for frequently accessed items.

```python
# Retrieve by ID
retrieved_bookmark = service.get_bookmark(bookmark.id)

if retrieved_bookmark:
    print(f"Retrieved: {retrieved_bookmark.title}")
```

When you call `get_bookmark`, the service first checks the cache. If the item is missing, it fetches it from the `BookmarkRepository` and populates the cache for future requests.

### Step 4: Perform a Full-Text Search

The service integrates with a `SearchIndex` to allow you to find bookmarks based on their content.

```python
# Search for bookmarks containing "Etchblok"
results = service.full_text_search("Etchblok", limit=5)

for result in results:
    print(f"Found: {result.title} ({result.url})")
```

The `full_text_search` method returns a list of `Bookmark` objects that match the query across titles, descriptions, and URLs.

### Step 5: Organize with Tags

You can also manage tags through the same service. Like bookmarks, tag creation follows the result/error tuple pattern.

```python
from app.models.tag import TagColor

tag_data = {
    "name": "Open Source",
    "color": "blue"
}

tag, error = service.create_tag(tag_data)

if not error:
    print(f"Created tag '{tag.name}' with color {tag.color.value}")
```

### Complete Example

Here is how these steps look when combined into a single workflow:

```python
from app.services.bookmark_service import BookmarkService

def main():
    service = BookmarkService()

    # 1. Create
    data = {"url": "https://python.org", "title": "Python Language"}
    bookmark, err = service.create_bookmark(data)
    
    if err:
        print(f"Error: {err}")
        return

    # 2. Retrieve (uses cache)
    found = service.get_bookmark(bookmark.id)
    
    # 3. Search
    search_results = service.full_text_search("Python")
    
    # 4. Cleanup (Soft-delete)
    # This moves the bookmark to 'trash' status rather than deleting from DB
    success = service.delete_bookmark(bookmark.id)
    
    print(f"Workflow complete. Bookmark trashed: {success}")

if __name__ == "__main__":
    main()
```

### Next Steps
- Explore **Collection Operations** using `service.create_collection()` and `service.add_to_collection()`.
- Learn about **Soft Deletion** and how to use `service.restore_bookmark()` to bring items back from the trash.
- Implement **Tag Management** to strip tags from bookmarks using `service.delete_tag()`.