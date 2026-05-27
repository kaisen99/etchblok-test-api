---
section_type: guide
---
Pagemark API is a bookmark management REST API built with Flask. It provides a layered architecture for managing bookmarks, tags, and collections with built-in full-text search and caching.

## Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)

## Installation

1. **Clone the repository** (if you haven't already).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Hello World / Quick Start

### 1. Run the Server
Start the Flask development server using the provided entry point:

```bash
python run.py
```
The API will be available at `http://localhost:5000`.

### 2. Create Your First Bookmark
Use `curl` to save a new URL to the API:

```bash
curl -X POST http://localhost:5000/api/bookmarks/ \
     -H "Content-Type: application/json" \
     -d '{"url": "https://flask.palletsprojects.com", "title": "Flask Documentation"}'
```

### 3. List All Bookmarks
Retrieve your saved bookmarks:

```bash
curl http://localhost:5000/api/bookmarks/
```

### Programmatic Usage
If you are extending the API or using its internal services, you can interact with the `BookmarkService` singleton:

```python
from app.services.bookmark_service import BookmarkService

# Initialize the service
service = BookmarkService()

# Create a bookmark programmatically
bookmark, error = service.create_bookmark({
    "url": "https://python.org",
    "title": "Python Language"
})

if not error:
    print(f"Created bookmark: {bookmark.id}")

# Search for bookmarks
results = service.search("Python")
for b in results:
    print(f"Found: {b.title} ({b.url})")
```

## Configuration

The application uses environment variables for configuration. You can set these in a `.env` file or directly in your shell.

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Used for session security and signing. | `change-me` |
| `FLASK_ENV` | Set to `development` or `production`. | `development` |

To run in production mode:
```bash
export SECRET_KEY="your-secure-random-key"
# Use a production WSGI server like gunicorn
gunicorn "app:create_app(config_class='app.config.ProductionConfig')"
```

## Verify Installation

You can verify that the API is running and healthy by hitting the internal health check endpoint:

```bash
curl http://localhost:5000/_internal/health
```
**Expected Response:**
```json
{"status": "ok"}
```

To check if the core services (Repository, Search, Cache) are ready:
```bash
curl http://localhost:5000/_internal/ready
```

## Next Steps

- Explore the [Bookmark Management System](/architecture/architecture-overview/bookmark-management-system-context) features including tagging and collections.
- Learn about the [Search Service](/api_ref/app/search_service) for full-text indexing.
- Review the [API Architecture](/architecture/architecture-overview/bookmark-api-component-architecture) for a complete list of available operations.
- Check the `app.config` module for advanced tuning of cache TTL and page sizes.
