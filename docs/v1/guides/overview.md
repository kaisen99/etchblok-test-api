---
section_type: guide
---
Pagemark API is a lightweight, developer-friendly bookmark management service built with Flask. It provides a robust REST interface for saving, organizing, and searching URLs with metadata, tagging, and collection support.

## The Problem
Managing bookmarks across different browsers and devices often leads to fragmented data and poor searchability. Pagemark API solves this by providing a centralized, programmable backend for bookmark storage. It is designed for developers who want to build their own bookmarking tools, browser extensions, or internal knowledge bases without worrying about the underlying storage and search logic.

## Core Concepts

*   **Bookmark**: The primary entity representing a saved URL. It includes a title, description, status (Active, Archived, or Trashed), and custom metadata.
*   **Tag**: A flexible, flat labeling system. Tags can be shared across bookmarks and have customizable colors.
*   **Collection**: A hierarchical grouping mechanism (though currently implemented as flat named groups) to organize bookmarks into logical sets like "Work," "Reading List," or "Project X."
*   **Search Index**: An in-memory inverted index that provides full-text search capabilities across bookmark titles and descriptions.
*   **Status Lifecycle**: Bookmarks follow a simple lifecycle: they start as `ACTIVE`, can be moved to `ARCHIVED` for long-term storage, or `TRASHED` for soft-deletion.

## How It Works

The application follows a clean, layered architecture to ensure separation of concerns:

1.  **Routes Layer**: Flask Blueprints (e.g., `bookmarks_bp`) handle HTTP request parsing and response formatting.
2.  **Service Layer**: The `BookmarkService` (a singleton) acts as the central orchestrator. It handles business logic, validation, and coordinates between the repository, cache, and search index.
3.  **Repository Layer**: The `BookmarkRepository` abstracts data access. In its current form, it provides in-memory storage, making it extremely fast for development and testing.
4.  **Search & Cache**: As bookmarks are created or updated, the `SearchIndex` incrementally updates its inverted index, and the `LRUCache` ensures frequently accessed bookmarks are served with minimal latency.

## Use Cases

### Creating a Bookmark
You can programmatically save a new bookmark by interacting with the `BookmarkService`.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark, error = service.create_bookmark({
    "url": "https://github.com",
    "title": "GitHub",
    "description": "Where the world builds software",
    "tags": ["dev", "git"]
})

if not error:
    print(f"Saved: {bookmark.id}")
```

### Searching Bookmarks
The API provides a simple full-text search that AND-s tokens together for precise results.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
results = service.search("software development")

for b in results:
    print(f"Found: {b.title} ({b.url})")
```

### Organizing with Collections
Group related bookmarks into named collections for better discoverability.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
# Create a collection
collection, _ = service.create_collection({"name": "Research Papers"})

# Add a bookmark to it
service.add_to_collection(collection.id, "some-bookmark-id")
```

## When to Use / When Not to Use

**Use Pagemark API when:**
*   You are building a personal bookmarking tool or a small-team knowledge base.
*   You need a lightweight, easy-to-deploy REST API for URL management.
*   You want a "batteries-included" backend with search and tagging out of the box.

**Look elsewhere if:**
*   You require persistent storage across restarts (the current repository is in-memory).
*   You need advanced multi-user permissions or OAuth2 authentication (this is a flat API).
*   You are managing millions of bookmarks (the in-memory search index is optimized for thousands, not millions).

## Stack Compatibility
*   **Language**: Python 3.8+
*   **Framework**: Flask 3.0+
*   **Dependencies**: `python-dotenv` for configuration.
*   **Storage**: In-memory (pluggable via `BookmarkRepository`).

## Getting Started Pointers
*   Explore the [API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture) for a full list of available REST actions.
*   Check the [Bookmark Model](/api_ref/app/models/bookmark/bookmark) to understand the data structure and metadata capabilities.
*   See the [SearchIndex](/api_ref/app/services/search/service/searchindex) implementation to learn how the full-text search is handled.

## Limitations & Assumptions
*   **Volatility**: Data is stored in memory and will be lost when the server restarts.
*   **Single Tenant**: The API assumes a single-user or shared-environment model; there is no built-in user isolation.
*   **Validation**: URL validation is basic (checks for `http/https` prefixes).

## FAQ

**How do I persist my data?**
Currently, the `BookmarkRepository` uses in-memory dictionaries. To persist data, you would need to implement a new repository class (e.g., `SQLiteRepository`) that follows the same interface.

**Does it support nested tags?**
No, tags are currently a flat list of strings associated with each bookmark.

**Can I search by tag?**
While there isn't a dedicated search endpoint for tags, you can list bookmarks and filter them, or use the `get_bookmarks_with_tag` method in the repository/service layer.

**Is there a frontend included?**
No, Pagemark API is a headless REST API. It is designed to be consumed by browser extensions, mobile apps, or web frontends.

**How does the caching work?**
It uses a simple LRU (Least Recently Used) cache in the service layer to store the most recently accessed `Bookmark` objects, reducing repository lookups.
