---
section_type: guide
---
Pagemark API is a lightweight, developer-friendly REST service for managing bookmarks. It provides a structured way to save URLs, organize them with tags and collections, and find them instantly using a built-in full-text search engine.

## Centralized Bookmark Management

Managing bookmarks across different browsers and devices often leads to fragmented, unsearchable lists. Pagemark API centralizes bookmark storage into a single, programmable interface. It solves the "where did I save that?" problem by providing a robust search index and flexible organization through tags and collections, making it ideal for building personal bookmarking tools, browser extensions, or knowledge management systems.

## Core Concepts

- **Bookmarks**: The primary entity, representing a saved URL with a title, description, and metadata.
- **Tags**: Flexible, color-coded labels that can be attached to multiple bookmarks for cross-cutting organization.
- **Collections**: Named groups used to categorize bookmarks into specific projects or topics (e.g., "Recipes", "Work", "Reading List").
- **Status Lifecycle**: Bookmarks move through `active`, `archived`, and `trashed` states, allowing for soft-deletion and long-term storage without cluttering the main view.
- **Search Index**: An inverted index that automatically indexes titles and descriptions for fast, keyword-based retrieval.

## How It Works

The application follows a layered architecture designed for clarity and extensibility:

1.  **Request Handling**: Flask blueprints in `app.routes` receive HTTP requests and parse incoming JSON or query parameters.
2.  **Service Orchestration**: The `BookmarkService` (a singleton facade) validates data and coordinates actions between the repository, search index, and cache.
3.  **In-Memory Storage**: The `BookmarkRepository` manages the lifecycle of entities in memory, providing a clean abstraction for future database integrations.
4.  **Full-Text Search**: As bookmarks are created or updated, the `SearchIndex` tokenizes their content and updates an inverted index for instant lookups.
5.  **LRU Caching**: Frequently accessed bookmarks are stored in an `LRUCache` to minimize repository lookups and improve response times.

## Use Cases

### Creating a Bookmark
```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark, error = service.create_bookmark({
    "url": "https://github.com",
    "title": "GitHub",
    "description": "Where the world builds software"
})
```

### Searching Bookmarks
```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
# Search across titles and descriptions
results = service.full_text_search("software", limit=5)
for b in results:
    print(f"Found: {b.title} ({b.url})")
```

### Organizing with Tags
```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()

# Create a color-coded tag
tag, _ = service.create_tag({"name": "development", "color": "blue"})

# Update bookmark with the new tag ID
service.update_bookmark(bookmark_id="abc123", data={"tags": [tag.id]})
```

## When to Use

- **Use when**:
    - Building a personal bookmarking tool or browser extension.
    - You need a simple, self-contained API for URL management.
    - You want a lightweight service with built-in search and caching.
- **Don't use when**:
    - You require persistent storage across restarts (current implementation is in-memory).
    - You need multi-user authentication and authorization.
    - You are managing millions of bookmarks (the in-memory index is optimized for small to medium datasets).

## Stack Compatibility

- **Language**: Python 3.x
- **Framework**: Flask 3.0+
- **Dependencies**: `python-dotenv` for configuration.
- **Storage**: In-memory (pluggable repository pattern).

## Getting Started Pointers

- **API Endpoints**: See the full list of available REST endpoints in the `README.md`.
- **Bookmark Model**: Explore the `app.models.bookmark.Bookmark` dataclass and its attributes.
- **BookmarkService**: The `app.services.bookmark_service.BookmarkService` is the main entry point for all business logic.

## Limitations & Assumptions

- **Volatility**: All data is lost when the server restarts as it uses in-memory storage.
- **Single User**: The API does not currently support multiple user accounts or permissions.
- **Validation**: Basic URL and title validation is performed, but it does not check if the URL is reachable.

## FAQ

**How do I persist data?**
Currently, the API uses an in-memory repository. To persist data, you would need to implement a new `BookmarkRepository` in `app.db.repository` that interfaces with a database like SQLite or PostgreSQL.

**Is the search case-sensitive?**
No, the `SearchIndex` tokenizes and searches text in a case-insensitive manner.

**What happens when I delete a tag?**
When a tag is deleted via `BookmarkService.delete_tag`, it is automatically stripped from all bookmarks that were using it before the tag itself is removed.

**Can a bookmark belong to multiple collections?**
Yes. You can add a bookmark to multiple collections by calling `add_to_collection` for each target collection.

**How does the cache work?**
It uses a Least-Recently-Used (LRU) strategy with a default size of 256 items. It is automatically invalidated whenever a bookmark is updated or deleted to ensure data consistency.
