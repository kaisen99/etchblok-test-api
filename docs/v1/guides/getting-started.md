---
section_type: guide
---
Pagemark API is a bookmark management service built with Flask. It provides a RESTful interface for saving, organizing, and searching bookmarks with support for tagging and collections.

## Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)

## Installation

1. **Clone the repository** (if you haven't already).
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Hello World / Quick Start

### 1. Start the API Server

Run the application using the provided entry point:

```bash
python run.py
```

The server will start on `http://localhost:5000` with debug mode enabled.

### 2. Create Your First Bookmark

Open a new terminal and use `curl` to save a bookmark:

```bash
curl -X POST http://localhost:5000/api/bookmarks/ \
     -H "Content-Type: application/json" \
     -d '{"url": "https://flask.palletsprojects.com/", "title": "Flask Documentation"}'
```

### 3. List All Bookmarks

Retrieve your saved bookmarks:

```bash
curl http://localhost:5000/api/bookmarks/
```

## Configuration

The application uses environment variables for configuration. These are defined in `app/config.py`.

| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `SECRET_KEY` | Used for session security and signing. | `change-me` |
| `FLASK_DEBUG` | Enables debug mode if set to `1`. | `True` (in `run.py`) |

For production, ensure you set a secure `SECRET_KEY`:
```bash
export SECRET_KEY='your-secure-random-string'
```

## Verify Installation

You can verify that the service is running and healthy by hitting the internal health endpoint:

```bash
curl http://localhost:5000/_internal/health
```

**Expected Response:**
```json
{"status": "ok"}
```

To check if the core services (like the `BookmarkService`) are ready:
```bash
curl http://localhost:5000/_internal/ready
```

## Next Steps

- **Organize with Tags**: Use the `/api/tags` endpoints to create and manage tags for your bookmarks.
- **Group into Collections**: Use the `/api/collections` endpoints to group related bookmarks together.
- **Search**: Use the `/api/bookmarks/search?q=query` endpoint to perform full-text searches across your saved titles and descriptions.
- **Explore the Architecture**: The project follows a layered architecture. Check out `app/services/bookmark_service.py` for the core business logic or `app/models/bookmark.py` for the data structure.
