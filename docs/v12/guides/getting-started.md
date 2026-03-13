---
section_type: guide
---
# Getting started

Pagemark API is a bookmark management REST API built with Flask. It allows you to save, organize, and search bookmarks using tags and collections.

## Prerequisites

- **Python 3.8+**: Required for Flask 3.0+.
- **pip**: Python package installer.

## Install

The fastest way to get Pagemark API running is using a virtual environment and `pip`.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run the server

Start the API server using the provided run script. By default, the server listens on `http://localhost:5000`.

```bash
python run.py
```

## Verify

You can verify the API is running by hitting the internal health endpoint or listing bookmarks (which will be empty initially).

```bash
# Check internal health
curl http://localhost:5000/_internal

# List bookmarks
curl http://localhost:5000/api/bookmarks
```

## Troubleshooting

- **Port 5000 in use**: If the server fails to start because the port is occupied (common on macOS), ensure no other Flask apps or AirPlay Receiver services are running on that port.
- **Missing Secret Key**: While the app provides a default, you can set a custom key in your environment:
  ```bash
  export SECRET_KEY="your-secure-key-here"
  ```

## Next steps

- Explore the full list of available [API Reference](/api_ref/app)
- Learn how to organize bookmarks with the [Collections and Smart Filtering](/guides/domain-models/collections-and-smart-filtering)
- Review the [Architecture Overview](/architecture/architecture-overview) to understand the service and repository layers