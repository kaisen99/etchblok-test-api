---
title: Getting Started with Local Development
description: A step-by-step tutorial for newcomers to set up their local environment using the development configuration class.
code_symbols: [SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: 5f5f3438-29be-4fd2-8821-1af5cec0bf66_getting_started_with_local_development
doc_type: tutorial
section_type: guide
---
In this tutorial, you will set up a local development environment for the Pagemark API. You will learn how the application uses the `DevelopmentConfig` class to enable debugging features and optimize settings for rapid iteration.

By the end of this guide, you will have a running local server configured with development-specific cache and pagination settings.

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.7+
- Flask
- The project dependencies (installable via `pip install -r requirements.txt`)

### Step 1: Explore the Base Configuration

The Pagemark API uses a class-based configuration system defined in `app/config.py`. All environment configurations inherit from `BaseConfig`, which establishes the core settings for the application.

Open `app/config.py` to see the foundation:

```python
from dataclasses import dataclass, field
import os

@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "change-me"))
    DEBUG: bool = False
    TESTING: bool = False
    PAGE_SIZE: int = 25  # Defined by DEFAULT_PAGE_SIZE in the file

    def get_cache_config(self) -> dict:
        """Return cache settings for this environment."""
        return {"ttl_seconds": 300, "max_entries": 1024, "eviction": "lru"}
```

The `BaseConfig` provides sensible defaults, such as a fallback `SECRET_KEY` of `"change-me"`. This allows the application to start locally without requiring you to set environment variables immediately.

### Step 2: Configure for Local Development

For local work, you use the `DevelopmentConfig` class. This class inherits from `BaseConfig` and overrides specific attributes to make debugging easier and feedback loops faster.

In `app/config.py`, the `DevelopmentConfig` is defined as follows:

```python
@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> dict:
        # Overrides base with shorter TTL (30s) and smaller size (128)
        return {"ttl_seconds": 30, "max_entries": 128, "eviction": "lru"}
```

By setting `DEBUG: bool = True`, the application provides detailed error pages and enables the Flask reloader. The `PAGE_SIZE` is reduced to `10` to make it easier to test pagination logic with fewer records.

### Step 3: Initialize the Application Factory

The application is created using a factory function in `app/__init__.py`. This factory is designed to use `DevelopmentConfig` by default, ensuring that anyone starting the project for the first time gets the correct development settings.

```python
from flask import Flask
from app.config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ... blueprint registration ...
    
    return app
```

The `app.config.from_object(config_class)` call reads the attributes from your configuration class and applies them to the Flask `app.config` dictionary.

### Step 4: Launch the Development Server

To start the API, use the `run.py` script located in the root directory. This script calls the `create_app()` factory without arguments, triggering the default `DevelopmentConfig`.

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

Run the server from your terminal:

```bash
python run.py
```

You should see output indicating that the server is running on `http://127.0.0.1:5000` with the debugger active.

### Step 5: Verify the Configuration

Once the server is running, you can verify that the configuration is active by checking the internal health endpoint. Open your browser or use `curl` to access:

```bash
curl http://127.0.0.1:5000/_internal/health
```

If the server responds with a `200 OK`, your local environment is correctly initialized using the `DevelopmentConfig` settings.

### Step 6: Customize via Environment Variables

While `DevelopmentConfig` provides a default `SECRET_KEY`, you can override it locally to match your specific needs without changing the code. Because `BaseConfig` uses `os.environ.get`, you can set the variable in your terminal before running the app:

```bash
export SECRET_KEY="my-local-secret"
python run.py
```

The application will now use `"my-local-secret"` instead of the default `"change-me"`. This is a useful pattern for testing how the application handles different environment configurations before moving to production.