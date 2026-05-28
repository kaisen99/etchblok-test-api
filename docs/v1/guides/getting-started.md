---
section_type: guide
---
Pagemark API is a bookmark management REST API built with Flask. It provides a layered architecture for saving, organizing, and searching bookmarks with support for tagging and collections.

## Prerequisites

- **Python 3.8+**: The application uses modern Python features and Flask 3.0.
- **pip**: Python package manager.

## Installation

1. **Clone the repository** and navigate to the project root:
   ```bash
   cd pagemark-api
   ```

2. **Install dependencies**:
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

### 2. Create a Bookmark
Use `curl` to save your first URL:
```bash
curl -X POST http://localhost:5000/api/bookmarks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://flask.palletsprojects.com",
    "title": "Flask Documentation",
    "description": "The official documentation for the Flask web framework.",
    "tags": ["python", "web", "docs"]
  }'
```

### 3. List Bookmarks
Retrieve all saved bookmarks:
```bash
curl http://localhost:5000/api/bookmarks
```

## Configuration

The application uses environment variables for configuration. You can set these in your shell or a `.env` file.

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Used for session security and signing. | `change-me` |
| `PAGE_SIZE` | Default number of items per page for lists. | `10` (Dev) / `25` (Prod) |

> **Note**: In production, you **must** set a secure `SECRET_KEY` environment variable.

## Verify Installation

You can verify the service status and connectivity using the internal health check endpoint:

```bash
curl http://localhost:5000/_internal/health
```

A successful installation will return:
```json
{"status": "ok"}
```

For a more thorough check that verifies the [Service Orchestration](/guides/service-orchestration) and [Repository Architecture](/guides/persistence-layer/repository-architecture) are initialized, use the readiness probe:
```bash
curl http://localhost:5000/_internal/ready
```

## Next Steps

- **Organize with Tags**: Learn how to manage [Creating and Managing Tags](/guides/categorization-collections/creating-and-managing-tags) to categorize your bookmarks.
- **Group into Collections**: Use [Understanding Collections](/guides/categorization-collections/understanding-collections) to group related bookmarks together.
- **Search**: Utilize the [Implementing Full-Text Search](/guides/service-orchestration/implementing-full-text-search) capabilities to find bookmarks by title or description.
- **Architecture**: Understand the [Architecture Overview](/architecture/architecture-overview) (Routes, Services, Repository) to extend the API.

## Troubleshooting

- **Data Persistence**: The current implementation uses an in-memory [Repository Architecture](/guides/persistence-layer/repository-architecture). All data will be lost when the server process restarts.
- **Port Conflicts**: If `5000` is already in use, you can modify the `port` argument in `run.py`.
- **Missing Dependencies**: Ensure you are using a virtual environment to avoid conflicts with system-level Python packages.
