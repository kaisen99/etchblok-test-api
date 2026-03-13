---
title: Core Services
description: The primary business logic layer providing a facade for managing the lifecycle of bookmarks, tags, and collections.
code_symbols: [SYM#dd5fd545693e00d6c0b38892bbd18ed4afa136a1]
section_id: 0969bdf9-2e8b-44c9-98c0-8398d7344a81_core_services
doc_type: how_to
section_type: guide
---
The **Core Services** layer provides a unified facade for managing the lifecycle of bookmarks, tags, and collections. The primary entry point is the `BookmarkService`, which orchestrates data persistence, in-memory caching, and full-text indexing.

## Managing Bookmarks

The `BookmarkService` handles the creation, retrieval, and modification of bookmarks while ensuring that the search index and cache remain synchronized.

### Creating and Updating Bookmarks

To create or update a bookmark, pass a dictionary of data to the service. The service performs validation using internal helpers like `_validate_url` and `_validate_title` before persisting the data.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Creating a bookmark
data = {
    "url": "https://example.com",
    "title": "Example Site",
    "description": "A useful reference"
}
bookmark, error = service.create_bookmark(data)

if error:
    print(f"Validation failed: {error}")
else:
    print(f"Created bookmark: {bookmark.id}")

# Updating an existing bookmark
update_data = {"title": "Updated Example Site"}
updated_bookmark, error = service.update_bookmark(bookmark.id, update_data)
```

When `create_bookmark` or `update_bookmark` is called, the service automatically:
1. Validates the input data.
2. Saves the entity to the `BookmarkRepository`.
3. Updates the `SearchIndex` for full-text searchability.
4. Invalidates the corresponding entry in the `LRUCache`.

### Deleting and Archiving

The service supports soft-deletion (trashing) and archiving.

```python
# Soft-delete (move to trash)
success = service.delete_bookmark(bookmark_id)

# Archive a bookmark
archived = service.archive_bookmark(bookmark_id)

# Restore a bookmark to active status
restored = service.restore_bookmark(bookmark_id)
```

## Full-Text Search

The `BookmarkService` provides a `search` method that leverages an in-memory `SearchIndex`. It tokenizes the query, removes stop words (e.g., "the", "and"), and ranks results based on token frequency in the title and description.

```python
# Search for bookmarks matching a query
results = service.search("example reference", limit=10)

for bookmark in results:
    print(f"Found: {bookmark.title} ({bookmark.url})")
```

The search implementation in `SearchIndex.search` ANDs tokens together, meaning all search terms must appear in the bookmark for it to be returned as a result.

## Tag and Collection Management

The service manages the relationship between bookmarks and their organizational metadata.

### Tag Lifecycle and Cascading Deletes

When a tag is deleted via `delete_tag`, the service performs a cascading cleanup to maintain data integrity. It iterates through all bookmarks associated with that tag, removes the reference, and invalidates their cache entries.

```python
# Create a new tag
tag, error = service.create_tag({"name": "Research", "color": "blue"})

# Delete a tag (triggers cascading cleanup)
# This removes the tag from all bookmarks that use it
success = service.delete_tag(tag.id)
```

### Managing Collections

Collections are managed by adding or removing bookmark IDs.

```python
# Create a collection
collection, error = service.create_collection({"name": "Project Alpha"})

# Add a bookmark to the collection
service.add_to_collection(collection.id, bookmark.id)

# Remove a bookmark from the collection
service.remove_from_collection(collection.id, bookmark.id)
```

## Internal Performance Components

The `BookmarkService` initializes two internal components to optimize performance and searchability:

1.  **LRUCache**: A fixed-capacity (256 items) cache used in `get_bookmark`. It tracks hits and misses and automatically evicts the least recently used bookmarks.
2.  **SearchIndex**: An inverted index mapping tokens to bookmark IDs. It is rebuilt from the repository on startup and updated incrementally during CRUD operations.

```python
# Internal initialization in BookmarkService._init_services
self._repo = BookmarkRepository()
self._cache = LRUCache(max_size=256)
self._search = SearchIndex(self._repo)
```

## Troubleshooting and Gotchas

### Singleton State
`BookmarkService` is implemented as a Singleton. This means the `LRUCache` and `SearchIndex` are shared across the entire application process. If you are running multiple worker processes (e.g., with Gunicorn), each process will have its own independent cache and search index.

### Performance of Tag Deletion
Deleting a tag is an $O(N)$ operation, where $N$ is the number of bookmarks associated with that tag. The service must load every affected bookmark to remove the tag reference and update the cache:

```python
# From app/services/bookmark_service.py
for bookmark in self._repo.get_bookmarks_with_tag(tag_id):
    bookmark.remove_tag(tag_id)
    self._repo.save_bookmark(bookmark)
    self._cache.invalidate(bookmark.id)
```

### Search Index Limitations
The `SearchIndex` is entirely in-memory. While efficient for small to medium datasets, it is rebuilt from the repository every time the service is initialized. Large datasets may lead to increased startup times and memory consumption.