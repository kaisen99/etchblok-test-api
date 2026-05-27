---
section_type: guide
---
Pagemark API is a lightweight, developer-friendly REST API for managing bookmarks. Built with Flask, it provides a structured way to save URLs, organize them with tags and collections, and find them instantly using a built-in full-text search engine.

## The Problem
Managing a growing list of links often leads to "bookmark rot"—where URLs are saved but never found again. Pagemark API solves this by providing a clean, layered backend that treats bookmarks as first-class entities with metadata, lifecycle states (active/archived/trashed), and powerful searchability, making it an ideal foundation for personal link-saving tools or browser extensions.

## Core Concepts

*   **Bookmarks**: The primary entity. Each bookmark tracks a URL, title, description, and its current [Bookmark Lifecycle States](/architecture/architecture-overview/bookmark-lifecycle-states).
*   **Tags**: Flexible, flat labels (e.g., "work", "recipe", "python") that can be attached to any number of bookmarks for cross-cutting organization.
*   **Collections**: Named groups of bookmarks. They can be **Manual** (you explicitly add bookmarks) or **Smart** (defined by a filter rule, though currently these act as containers).
*   **Lifecycle Status**: Bookmarks move through states: `active` (visible), `archived` (hidden from main lists), and `trashed` (soft-deleted).
*   **In-Memory Storage**: By default, the API uses a volatile in-memory repository, making it extremely fast and easy to reset during development.

## How It Works
The application follows a classic layered architecture designed for testability and separation of concerns:

1.  **Routes (Blueprints)**: Flask blueprints in `app/routes/` handle HTTP parsing and response serialization.
2.  **Service Layer**: The `BookmarkService` (a singleton) acts as the central brain, orchestrating validation, search indexing, and cache management.
3.  **Repository**: The `BookmarkRepository` abstracts data access. While currently in-memory, it is designed to be swapped for a persistent database like SQLite or PostgreSQL.
4.  **Search Index**: An internal `SearchIndex` maintains an inverted index of tokens from titles and descriptions to provide fast full-text search without external dependencies like Elasticsearch.
5.  **Caching**: An `LRUCache` sits in front of the repository to speed up retrieval of frequently accessed bookmarks.

## Use Cases

### Creating a Bookmark
Save a new URL with a title and optional description.

```python
import requests

payload = {
    "url": "https://flask.palletsprojects.com/",
    "title": "Flask Documentation",
    "description": "The official docs for the Flask web framework."
}
response = requests.post("http://localhost:5000/api/bookmarks/", json=payload)
print(response.json())
```

### Searching Your Links
Find bookmarks using the built-in full-text search engine.

```bash
# Search for "flask" in titles and descriptions
curl "http://localhost:5000/api/bookmarks/search?q=flask"
```

### Organizing with Tags
Create tags and associate them with your bookmarks.

```python
# Create a tag
tag_data = {"name": "development", "color": "blue"}
requests.post("http://localhost:5000/api/tags/", json=tag_data)

# Tags are then referenced by their ID in bookmark updates
```

## When to Use
*   **Prototyping**: Perfect for building a frontend for a bookmarking app without worrying about DB setup.
*   **Internal Tools**: Use it as a backend for a team-wide "useful links" dashboard.
*   **Learning**: An excellent reference for implementing a clean, layered architecture in Flask with services and repositories.

## When Not to Use
*   **Persistent Storage**: Since it is in-memory, all data is lost when the server restarts.
*   **Multi-user Environments**: There is no built-in authentication or user isolation.
*   **Large Datasets**: The in-memory search and storage are optimized for thousands, not millions, of records.

## Stack Compatibility
*   **Language**: Python 3.10+
*   **Framework**: Flask 3.0+
*   **Dependencies**: `python-dotenv` for configuration management.
*   **Storage**: Volatile In-Memory (Default).

## Getting Started Pointers
*   Explore the [Bookmark API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture) for a full list of available operations.
*   Check `app/config.py` to adjust server settings.
*   See `app/models/bookmark.py` to understand the data structure.

## Limitations & Assumptions
*   **Volatile Data**: Data does not persist across restarts.
*   **Smart Collections**: The `filter_rule` logic is defined in the model but is not automatically applied by the current API endpoints; bookmarks must still be added manually.
*   **No Auth**: The API is completely open; it assumes it is running in a trusted environment or behind a proxy.

## FAQ

**How do I persist my data?**
Currently, the `BookmarkRepository` uses Python dictionaries. To persist data, you would need to implement a new repository class (e.g., `SQLiteBookmarkRepository`) that follows the same interface.

**Can I search by tag?**
The search endpoint currently focuses on full-text search of titles and descriptions. To filter by tag, you can use the `list_bookmarks` endpoint with custom logic or retrieve bookmarks directly via the repository's `get_bookmarks_with_tag` method.

**What happens when I delete a bookmark?**
The `DELETE /api/bookmarks/<id>` endpoint performs a "soft delete" by moving the bookmark to the `trashed` status. It is not removed from the memory until the server restarts.

**Is there a limit to how many bookmarks I can save?**
Only the limits of your system's RAM. The `LRUCache` is capped at 256 items by default, but the repository itself is unbounded.

**How does the search ranking work?**
The `SearchIndex` ranks results based on the frequency of query tokens appearing in the bookmark's title and description. It uses a simple "hit count" relevance score.
