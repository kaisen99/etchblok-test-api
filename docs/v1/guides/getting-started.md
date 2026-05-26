---
section_type: guide
---
The Pagemark API is a bookmark management service built with Flask. It provides a layered architecture for managing bookmarks, tags, and collections with built-in caching and full-text search.

## Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd pagemark-api
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Hello World / Quick Start

### 1. Start the Server
Run the application using the provided entry point:

```bash
python run.py
```
The API will be available at `http://localhost:5000`.

### 2. Create Your First Bookmark
Open a new terminal and use `curl` to save a bookmark:

```bash
curl -X POST http://localhost:5000/api/bookmarks/ \
     -H "Content-Type: application/json" \
     -d '{"url": "https://flask.palletsprojects.com/", "title": "Flask Documentation"}'
```

### 3. List Bookmarks
Retrieve all saved bookmarks:

```bash
curl http://localhost:5000/api/bookmarks/
```

## Configuration

The application uses environment variables for configuration. You can set these in your shell or a `.env` file.

| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `SECRET_KEY` | Used for session security and signing. | `change-me` |
| `FLASK_ENV` | Set to `production` or `development`. | `development` |

To run in production mode:
```bash
export SECRET_KEY="your-secure-key-here"
# Then run using a production WSGI server like gunicorn
pip install gunicorn
gunicorn "app:create_app()"
```

## Verify Installation

You can verify that the API and its internal services are running correctly by hitting the health check endpoint:

```bash
curl http://localhost:5000/_internal/health
# Expected response: {"status": "ok"}
```

For a deeper check that includes service initialization:
```bash
curl http://localhost:5000/_internal/ready
# Expected response: {"status": "ready"}
```

## Next Steps

- **Explore the API**: See the full list of endpoints in the [API Reference](/api_ref/app/routes/bookmarks/list_bookmarks) documentation.
- **Organize with Tags**: Learn how to create and assign tags to your bookmarks.
- **Group into Collections**: Use collections to group related bookmarks together.
- **Search**: Use the `/api/bookmarks/search?q=query` endpoint to perform full-text searches across your saved titles and descriptions.

## Troubleshooting

- **Port 5000 already in use**: If you see an error that the port is taken, you can change it in `run.py` or by setting the `FLASK_RUN_PORT` environment variable if using `flask run`.
- **Missing Secret Key**: In production mode, the application will fail to start if `SECRET_KEY` is not set. Ensure it is exported in your environment.
