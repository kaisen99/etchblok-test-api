---
section_type: guide
---
Pagemark API is a lightweight, developer-friendly REST service for managing bookmarks. Built with Flask, it provides a structured way to save URLs, organize them with tags and collections, and find them instantly using a built-in full-text search engine.

## The Problem
Web browsers have built-in bookmarking, but they are often silos—hard to search programmatically, difficult to organize with complex metadata, and not easily accessible via API for custom tools or dashboards. Pagemark API provides a standalone, headless service to centralize your "read later" lists and reference links in a way that is easy to integrate into your own workflows.

## Core Concepts

*   **Bookmarks**: The primary entity representing a saved URL. Each bookmark includes a title, description, and metadata.
*   **Tags**: Flexible, color-coded labels that can be attached to multiple bookmarks for cross-cutting organization.
*   **Collections**: Named groups used to cluster related bookmarks (e.g., "Project Research" or "Recipes").
*   **Status Lifecycle**: Bookmarks move through states: `ACTIVE` for daily use, `ARCHIVED` for long-term storage, and `TRASHED` for soft-deletion.
*   **Search Index**: An in-memory inverted index that allows for instant full-text search across titles and descriptions.

## How it Works

The application follows a classic layered architecture designed for maintainability and testability:

1.  **Route Layer**: Flask blueprints (in `app.routes`) handle HTTP request parsing and response formatting.
2.  **Service Layer**: The `BookmarkService` (a singleton) acts as the central orchestrator. It handles business logic, validation, and coordinates between the repository and the search index.
3.  **Repository Layer**: The `BookmarkRepository` abstracts data access. In the current version, this is an in-memory store, but it is designed to be swapped for a persistent database.
4.  **Search & Cache**: As bookmarks are saved, they are automatically indexed by the `SearchIndex` and cached in an `LRUCache` for high-performance retrieval.

## Use Cases

### Creating a Bookmark
You can save a new bookmark by sending a POST request. The service validates the URL and title before persisting it.

```python
# Example using the internal BookmarkService directly
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
bookmark, error = service.create_bookmark({
    "url": "https://github.com",
    "title": "GitHub",
    "description": "Where the world builds software"
})
```

### Searching Your Library
The API supports full-text search that ranks results based on token frequency in the title and description.

```bash
# Search for bookmarks containing "python"
curl http://localhost:5000/api/bookmarks/search?q=python&limit=5
```

### Organizing with Tags
Tags can be created and then attached to bookmarks to build a flexible taxonomy.

```python
from app.services.bookmark_service import BookmarkService

service = BookmarkService()
# Create a tag
tag, _ = service.create_tag({"name": "Programming", "color": "blue"})

# The service handles updating the bookmark and invalidating caches
service.update_bookmark(bookmark_id="abc123", data={"tags": [tag.id]})
```

## When to Use / When Not to Use

**Use Pagemark API if:**
*   You need a lightweight backend for a personal bookmarking tool.
*   You are prototyping a "read-it-later" application.
*   You want a simple, searchable index of links for a small team or internal project.

**Look elsewhere if:**
*   **Persistence is critical**: The current implementation uses in-memory storage; data is lost when the server restarts.
*   **Multi-user isolation**: There is currently no built-in authentication or user-scoping for data.
*   **Massive scale**: The in-memory search and repository are optimized for thousands, not millions, of entries.

## Stack Compatibility
*   **Language**: Python 3.10+
*   **Framework**: Flask 3.0+
*   **Storage**: In-memory (pluggable `BookmarkRepository` pattern)
*   **Search**: Custom in-memory inverted index

## Getting Started Pointers
*   To explore the API structure, see the Routes documentation.
*   For details on the data shapes, check the [Domain Models](/guides/domain-models) section.
*   To understand the core logic, read about the [BookmarkService](/api_ref/app/services/bookmark/service/bookmarkservice).

## Limitations
*   **Volatile Storage**: All data is stored in RAM. To persist data, you must implement a database-backed version of `BookmarkRepository`.
*   **No Auth**: The API is open by default. It is intended to run behind a proxy or on a local network.
*   **Single Instance**: Because the state is in-memory, you cannot scale this horizontally without a shared data store.

## FAQ

**How do I persist my bookmarks?**
Currently, the API resets on every restart. You would need to modify `app/db/repository.py` to use a database like SQLite or PostgreSQL.

**Does it support browser extensions?**
The REST API is compatible with standard browser extension patterns, but no official extension is provided in this repository.

**Can I search by tags?**
Yes, you can filter the bookmark list by status and retrieve bookmarks associated with specific tags via the service layer.

**Is there a UI?**
This is a headless API. You are expected to build your own frontend or use tools like Postman/cURL to interact with it.

**How does the search ranking work?**
The `SearchIndex` uses a simple token-frequency algorithm. It counts how many times your search terms appear in the title and description and sorts the results accordingly.
