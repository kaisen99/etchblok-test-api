---
section_type: guide
---
Pagemark API is a bookmark management REST service built with Flask. It provides a layered architecture for organizing URLs with tags and collections, featuring full-text search and in-memory caching.

## Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)

## Installation

1. Clone the repository and navigate to the project directory.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Hello World / Quick Start

To get the API up and running locally:

1. **Start the server**:
   ```bash
   python run.py
   ```
   The server will start on `http://localhost:5000` with debug mode enabled by default.

2. **Create your first bookmark**:
   Open a new terminal and use `curl` to save a URL:
   ```bash
   curl -X POST http://localhost:5000/api/bookmarks/ \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://flask.palletsprojects.com/",
       "title": "Flask Documentation",
       "description": "The official documentation for the Flask web framework."
     }'
   ```

3. **Retrieve all bookmarks**:
   ```bash
   curl http://localhost:5000/api/bookmarks/
   ```

## Configuration

The application uses environment variables for configuration. You can define these in a `.env` file in the root directory.

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Used for session security and signing. | `change-me` |
| `FLASK_ENV` | Set to `production` or `development`. | `development` |

In `app/config.py`, the `ProductionConfig` class requires `SECRET_KEY` to be set in the environment:

```python
# Example production environment variable
export SECRET_KEY="your-secure-random-string"
```

## Verify Installation

You can verify that the service is running and healthy by hitting the internal health check endpoint:

```bash
curl http://localhost:5000/_internal/health
```

Expected response:
```json
{"status": "ok"}
```

For a more detailed check that verifies service initialization, use the readiness probe:
```bash
curl http://localhost:5000/_internal/ready
```

## Next Steps

- **Explore the API**: See the full list of endpoints in the [API Reference](/api_ref/app) section of the README.
- **Understand the Architecture**: Learn about the [Flask API Layered Architecture](/architecture/architecture-overview/flask-api-layered-architecture) including Services, Repositories, and Models.
- **Search and Tags**: Learn how to use the [Overview of the Search Service](/guides/search-indexing/overview-of-the-search-service) and organize bookmarks with [Tagging and Metadata](/guides/core-entities/tagging-and-metadata).
