---
title: 'Quickstart: Configuring Your Application'
description: A step-by-step guide to setting up your first configuration file using the development defaults.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18, SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857]
section_id: e9f7fec5-9529-42ff-9df0-22422d15c576_quickstart-_configuring_your_application
doc_type: tutorial
section_type: guide
---
This guide walks you through setting up your local development environment using the built-in configuration defaults. You will learn how to initialize the application with `DevelopmentConfig`, verify its settings, and customize it for your local machine.

### Prerequisites

Before starting, ensure you have the following installed:
- Python 3.x
- Flask

### Step 1: Explore the Development Configuration

The application uses a class-based configuration system defined in `app/config.py`. The `DevelopmentConfig` class is specifically designed for local work, enabling debug features and adjusting performance settings for easier testing.

In `app/config.py`, you can see how `DevelopmentConfig` inherits from `BaseConfig`:

```python
@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)
```

By using this class, you automatically enable Flask's `DEBUG` mode and reduce the `PAGE_SIZE` to 10 (down from the default 25), which makes it easier to test pagination logic with fewer records.

### Step 2: Initialize the Application Factory

The application uses the factory pattern to create instances. The `create_app` function in `app/__init__.py` is configured to use `DevelopmentConfig` by default if no other configuration is provided.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory.

    Creates and configures the Flask application, registers blueprints,
    and initialises the in-memory database.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ... blueprint registration ...

    return app
```

This means you don't need to pass any arguments to `create_app()` when working locally; it will automatically pick up the development settings.

### Step 3: Launch the Application

To start the server with these settings, use the `run.py` entry point located in the root directory. This script calls the factory and starts the Flask development server.

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

When you run `python run.py`, the application starts on port 5000. Because `DevelopmentConfig` is active, the Flask debugger is enabled, allowing you to see detailed error pages in your browser if something goes wrong.

### Step 4: Customize via Environment Variables

While `DevelopmentConfig` provides sensible defaults, you may want to change sensitive values like the `SECRET_KEY`. The `BaseConfig` class (which `DevelopmentConfig` inherits from) is designed to look for an environment variable named `SECRET_KEY`.

In `app/config.py`:
```python
@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "change-me"))
    # ...
```

To use a custom key locally without modifying the code, set the environment variable before running the app:

```bash
export SECRET_KEY="your-custom-dev-key"
python run.py
```

The application will now use `"your-custom-dev-key"` instead of the default `"change-me"`.

### Verifying the Result

Once the application is running, you can verify the configuration is active:
1.  **Debug Mode**: Check your terminal output; you should see `* Debug mode: on`.
2.  **Pagination**: Access any list endpoint (e.g., `/api/bookmarks`). You will notice that the API returns a maximum of 10 items per page, confirming that the `PAGE_SIZE` from `DevelopmentConfig` is being applied.

### Next Steps
Now that your development environment is configured, you can begin exploring the API endpoints defined in `app/routes/bookmarks.py` or `app/routes/tags.py`. If you are ready to move towards a staging or production setup, look into `ProductionConfig` in `app/config.py`, which enforces stricter security requirements like a mandatory `SECRET_KEY`.
