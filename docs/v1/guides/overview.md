---
section_type: guide
---
Pagemark API is a lightweight, Flask-based REST service for managing bookmarks. It provides a structured way to save URLs, organize them with tags and collections, and perform full-text searches across your saved content.

## The Digital Hoarding Solution
Pagemark solves the "scattered tab" problem by providing a centralized repository for web resources. Instead of losing links in browser history or disparate note-taking apps, Pagemark offers a searchable, taggable, and programmable API to manage your digital library.

## Core Concepts

*   **Bookmarks**: The primary entity. Each bookmark contains a URL, title, description, and a lifecycle status (Active, Archived, or Trashed).
*   **Tags**: Flexible, color-coded labels (e.g., "Research", "To-Read") that can be applied across bookmarks for cross-cutting organization.
*   **Collections**: Named groups of bookmarks. These can be **Manual** (explicitly added) or **Smart** (automatically populated based on filter rules).
*   **Status Lifecycle**: A built-in workflow for moving bookmarks from active use to a long-term archive or a temporary trash bin for soft-deletion.

## How it Works
The application follows a clean, layered architecture designed for testability and separation of concerns:

1.  **Routes**: Flask blueprints (e.g., `bookmarks_bp`) handle HTTP request parsing and response formatting.
2.  **Service Layer**: The `BookmarkService` (a singleton) orchestrates business logic, including validation, cache management, and search indexing.
3.  **Repository**: The `BookmarkRepository` abstracts data access. In the current version, this is an **in-memory** store using Python dictionaries.
4.  **Search & Cache**: A dedicated `SearchIndex` provides full-text search capabilities, while an `LRUCache` ensures frequently accessed bookmarks are retrieved instantly.

## Use Cases

### Create a Bookmark
Save a new URL with a title and description.
```python
# POST /api/bookmarks/
{
    "url": "https://flask.palletsprojects.com/",
    "title": "Flask Documentation",
    "description": "The official documentation for the Flask web framework."
}
```

### Organize with Tags
Create a tag and attach it to a bookmark to group related content.
```python
# POST /api/tags/
{
    "name": "Python",
    "color": "blue"
}

# PUT /api/bookmarks/<id>
{
    "tags": ["python-tag-id"]
}
```

### Full-Text Search
Search across all your saved titles and descriptions.
```bash
# GET /api/bookmarks/search?q=flask
{
    "results": [...],
    "count": 1
}
```

### Smart Collections
Create a collection that automatically includes bookmarks matching a specific keyword.
```python
# POST /api/collections/
{
    "name": "Frameworks",
    "type": "smart",
    "filter_rule": "framework"
}
```

## When to Use
*   **Personal Tools**: Building a private bookmarking dashboard or browser extension.
*   **Prototyping**: Quickly testing bookmark-related features without setting up a heavy database.
*   **Learning**: Exploring a well-structured Flask application with a service-repository pattern.

## When Not to Use
*   **Persistent Storage**: Since the repository is in-memory, all data is lost when the server restarts. It is not suitable for long-term data retention without implementing a database-backed repository.
*   **High Concurrency**: The in-memory storage and singleton service pattern are not designed for high-traffic production environments.

## Integration & Stack
*   **Framework**: Flask 3.0+
*   **Language**: Python 3.x
*   **Dependencies**: `python-dotenv` for configuration management.
*   **Storage**: In-memory (pluggable repository pattern).

## Getting Started Pointers
*   Explore the [Bookmark Model](/api_ref/app/models/bookmark/bookmark) to see available metadata fields.
*   Check the [BookmarkService](/api_ref/app/services/bookmark/service/bookmarkservice) for the core business logic implementation.
*   Review the [API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture) in the README for a full list of available routes.

## FAQ
**Does it support persistent storage?**
Not out-of-the-box. The current `BookmarkRepository` is in-memory. However, the architecture is designed to allow swapping it with a SQL or NoSQL implementation.

**How does the search work?**
It uses a `SearchIndex` class that performs keyword matching across the `title` and `description` fields of all indexed bookmarks.

**What is a "Smart" collection?**
A smart collection uses a `filter_rule` (a simple keyword) to automatically group bookmarks. Any bookmark containing that keyword in its title or description is considered part of the collection.

**Can I recover deleted bookmarks?**
Yes. The `DELETE` endpoint performs a "soft-delete" by moving the bookmark to the `TRASHED` status. You can restore it using the `/restore` endpoint.