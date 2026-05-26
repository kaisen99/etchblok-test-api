---
section_type: guide
---
Pagemark API is a lightweight bookmark management service built with Flask. It provides a structured way to save, organize, and search URLs using a layered architecture that separates business logic from storage.

## The "Digital Filing Cabinet"
Managing thousands of browser bookmarks is often a mess of unsorted folders and broken links. Pagemark API solves this by treating bookmarks as first-class entities with rich metadata, flexible tagging, and full-text search.

Think of it as a **digital filing cabinet**:
- **Bookmarks** are the files (containing URLs, titles, and descriptions).
- **Tags** are the sticky labels you slap on files to find them across different contexts.
- **Collections** are the drawers where you group related files together.

## Core Concepts

- **Bookmarks**: The primary entity. Each bookmark tracks a URL, title, description, and its current status (Active, Archived, or Trashed).
- **Tags**: Flat labels used for cross-cutting organization. A bookmark can have many tags, and tags track their own usage counts.
- **Collections**: Groups of bookmarks. These can be **Manual** (you add items explicitly) or **Smart** (items are automatically included based on a filter rule).
- **Search Index**: An in-memory inverted index that allows for fast full-text search across all bookmark titles and descriptions.
- **LRU Cache**: A performance layer that keeps frequently accessed bookmarks in memory to reduce repository lookups.

## How It Works

The application follows a strict layered architecture to ensure maintainability:

1.  **Routes**: Flask Blueprints (in `app.routes`) handle HTTP request parsing and response formatting.
2.  **Service Layer**: The `BookmarkService` (a singleton) acts as the brain of the application. It orchestrates validation, cache invalidation, and search indexing.
3.  **Models**: Domain entities are defined as Python dataclasses (in `app.models`), ensuring type safety and easy serialization.
4.  **Repository**: The `BookmarkRepository` abstracts data access. While currently in-memory, this layer allows switching to a database without changing business logic.
5.  **Search & Cache**: Sidecar services that provide full-text search capabilities and performance optimizations.

## Use Cases

### Saving a new resource
Create a bookmark with metadata and tags via the API.

```python
# Example of the data structure used by BookmarkService.create_bookmark
new_bookmark = {
    "url": "https://flask.palletsprojects.com/",
    "title": "Flask Documentation",
    "description": "The official documentation for the Flask web framework.",
    "tags": ["python", "web", "docs"]
}
```

### Organizing with Smart Collections
Create a collection that automatically gathers all bookmarks mentioning "Python".

```python
from app.models.collection import Collection, CollectionType

smart_col = Collection(
    name="Python Resources",
    collection_type=CollectionType.SMART,
    filter_rule="python"
)
```

### Full-text Search
Find bookmarks using the internal search index.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
results = service.search("framework", limit=5)
# Returns a list of Bookmark objects matching the query
```

## When to Use / When Not to Use

**Use Pagemark API if:**
- You need a headless backend for a custom bookmarking tool or browser extension.
- You want a simple, hackable reference for a layered Flask architecture.
- You are building a personal knowledge base and need a structured URL store.

**Don't use Pagemark API if:**
- You require persistent storage out of the box (the current repository is in-memory and wipes on restart).
- You need multi-user support or complex authentication (this is a single-user API).
- You are handling millions of bookmarks (the in-memory search and repository are optimized for thousands, not millions).

## Integration & Stack

- **Framework**: Flask 3.0+
- **Language**: Python 3.10+
- **Storage**: In-memory (pluggable via `BookmarkRepository`)
- **Dependencies**: `python-dotenv` for configuration management.

## Getting Started Pointers

- **API Reference**: See the `app/routes/` directory for endpoint definitions.
- **Business Logic**: Explore `app.services.bookmark_service` for the core orchestration logic.
- **Data Structures**: Check `app.models.bookmark` for the primary data schema.

## Limitations & Assumptions

- **Volatility**: All data is lost when the server stops. You must implement a persistent `BookmarkRepository` (e.g., using SQLAlchemy) for production use.
- **Single User**: There is no concept of "ownership"; all bookmarks are visible to any client of the API.
- **Manual Indexing**: The search index is rebuilt on startup, which may cause a slight delay if the dataset is large.

## FAQ

**How do I change the storage to a database?**
You only need to create a new class that implements the same interface as `BookmarkRepository` in `app/db/repository.py` and update the `BookmarkService` to use it.

**Does it support nested tags?**
No, tags are currently a flat namespace.

**Can a bookmark be in multiple collections?**
Yes. Manual collections store a list of bookmark IDs, and a single ID can appear in any number of collections.

**How does the search ranking work?**
The `SearchIndex` ranks results based on the frequency of query tokens appearing in the title and description of the bookmark.

**Is there a frontend included?**
No, this is a pure REST API. It is designed to be consumed by a CLI, a web frontend, or a browser extension.
