---
section_type: guide
---
Pagemark API is a bookmark management REST API built with Flask. It provides a layered architecture for saving, organizing, and searching bookmarks with tagging and collections.

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

To get the API up and running locally:

1. **Start the server**:
   ```bash
   python run.py
   ```
   The API will start on `http://localhost:5000`.

2. **Create your first bookmark**:
   ```bash
   curl -X POST http://localhost:5000/api/bookmarks/ \
        -H "Content-Type: application/json" \
        -d '{"url": "https://github.com", "title": "GitHub", "description": "Where the world builds software"}'
   ```

3. **Retrieve all bookmarks**:
   ```bash
   curl http://localhost:5000/api/bookmarks/
   ```

## Configuration

The application uses environment variables for configuration. You can set these in a `.env` file or directly in your shell.

- `SECRET_KEY`: A secret key used for security. Defaults to `change-me` in development but is **required** in production.
- `DEBUG`: Set to `True` by default in development mode.

The application uses different configuration classes defined in `app/config.py`:
- `DevelopmentConfig`: Default, optimized for local work.
- `ProductionConfig`: Stricter settings for deployment.
- `TestingConfig`: Used for running tests.

## Verify Installation

You can verify that the service is running and ready to handle requests by hitting the internal health endpoints:

```bash
# Check liveness
curl http://localhost:5000/_internal/health

# Check readiness (verifies core services are initialized)
curl http://localhost:5000/_internal/ready
```

## Next Steps

- **Explore the API**: See the full list of endpoints in the [API Reference](/api_ref/app) section of the README.
- **Organize with Tags**: Create tags via `POST /api/tags` and associate them with your bookmarks.
- **Group into Collections**: Use the [Collections](/guides/categorization-and-collections) feature to group related bookmarks together.
- **Search**: Use the full-text search endpoint `GET /api/bookmarks/search?q=query` to find specific bookmarks.

## Troubleshooting

- **Port 5000 already in use**: If you see an error that port 5000 is occupied, you can change the port in `run.py` or set the `FLASK_RUN_PORT` environment variable if using `flask run`.
- **Missing SECRET_KEY**: If running in production mode, the app will fail to start if `SECRET_KEY` is not set in the environment.
