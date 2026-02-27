# Pagemark API

A bookmark management REST API built with Flask. Allows users to save, organize, and search bookmarks with tagging and collections.

## Features

- **Bookmark CRUD** — Save URLs with titles, descriptions, and metadata
- **Tagging** — Organize bookmarks with flexible tagging
- **Collections** — Group bookmarks into named collections
- **Full-text search** — Search across bookmark titles and descriptions
- **Caching** — In-memory LRU cache for frequently accessed bookmarks

## Architecture

The application follows a layered architecture:

- **Routes** — Flask blueprints handling HTTP requests and responses
- **Services** — Business logic layer with validation and orchestration
- **Repository** — Data access layer abstracting storage operations
- **Models** — Data classes representing domain entities

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

The API starts on `http://localhost:5000`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/bookmarks` | List all bookmarks |
| POST | `/api/bookmarks` | Create a bookmark |
| GET | `/api/bookmarks/<id>` | Get a bookmark |
| PUT | `/api/bookmarks/<id>` | Update a bookmark |
| DELETE | `/api/bookmarks/<id>` | Delete a bookmark |
| GET | `/api/bookmarks/search` | Search bookmarks |
| GET | `/api/tags` | List all tags |
| POST | `/api/tags` | Create a tag |
| DELETE | `/api/tags/<id>` | Delete a tag |
| GET | `/api/collections` | List collections |
| POST | `/api/collections` | Create a collection |
| PUT | `/api/collections/<id>/bookmarks` | Add bookmark to collection |
