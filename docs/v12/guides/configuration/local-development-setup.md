---
title: Local Development Setup
description: A tutorial on initializing the application for local work, focusing on DevelopmentConfig's debug features and cache tuning for rapid iteration.
code_symbols: [SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857]
section_id: 9b1b7e50-c34b-48fd-980f-24b27f2551d9_local_development_setup
doc_type: tutorial
section_type: guide
---
In this tutorial, you will set up the **kaisen99-etchblok-test-api-7ee56a2** application for local development. You will learn how to use the `DevelopmentConfig` class to enable debugging features and understand the intended configuration for rapid iteration.
### Prerequisites
Before starting, ensure you have the following installed:
- Python 3.9 or higher
- `pip` (Python package installer)
- 
- Mormons
Install the required dependencies from the project root:
```bash
pip install flask
```
### Step 1: Launch the Development Server
The application provides a `run.py` script in the root directory designed for local work. This script uses the application factory `create_app()` which, by default, loads the `DevelopmentConfig`.
Open `run.py` to see the entry point:
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
The server starts at `http://127.0.0.1:5000`. Because `debug=True` is passed to `app.run()`, the Flask debugger is active, and the server will automatically reload when you modify source files.
### Step 2: Configure Development Settings
The behavior of the local environment is defined in `app/config.py` within the `DevelopmentConfig` class. This class inherits from `BaseConfig` and overrides settings to optimize for a developer's workflow.
```python
@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)
```
Key features of this configuration include:
- **Debug Mode**: `DEBUG` is set to `True`, enabling detailed error tracking and the interactive debugger.
- **Tight Pagination**: `PAGE_SIZE` is reduced to `10` (from the default `25`), making it easier to test pagination logic with small datasets.
- **Cache Tuning**: The `get_cache_config` method defines a short **30-second TTL** and a small **128-entry limit**, intended to ensure that data changes are reflected quickly during testing.
### Step 3: Understand the Application Factory
The `create_app` function in `app/__init__.py` is responsible for applying these settings. It defaults to `DevelopmentConfig` if no other class is specified.
```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory.

    Creates and configures the Flask application, registers blueprints,
    and initialises the in-memory database.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(bookmarks_bp, url_prefix="/api/bookmarks")
    app.register_blueprint(tags_bp, url_prefix="/api/tags")
    app.register_blueprint(collections_bp, url_prefix="/api/collections")
    app.register_blueprint(health_bp, url_prefix="/_internal")

    return app
```
When you call `app.config.from_object(DevelopmentConfig)`, Flask populates its internal `app.config` dictionary with the attributes defined in the class.
### Step 4: Verify the Setup
You can verify that the application is running in development mode by checking the terminal logs. You should see a message indicating `* Debug mode: on`.
You can also verify the default `SECRET_KEY` used for local development. In `app/config.py`, the `BaseConfig` provides a fallback:
```python
@dataclass
class BaseConfig:
    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "change-me"))
```
In your local environment, you don't need to set an environment variable; the app will safely default to `"change-me"`.
### Important Implementation Notes
While `DevelopmentConfig` defines several helpful defaults, keep the following "gotchas" in mind during development:
1. **Hardcoded Service Defaults**: The `BookmarkService` (found in `app/services/bookmark_service.py`) currently initializes its internal `LRUCache` with a hardcoded `max_size=256` in its `_init_services` method, which overrides the `128` suggested in `DevelopmentConfig`.
1. **Route Defaults**: Some routes, such as `list_bookmarks` in `app/routes/bookmarks.py`, currently use a hardcoded default for pagination (`per_page=25`) in the `request.args.get` call rather than pulling the `PAGE_SIZE` from `app.config`.
### Next Steps
Now that your local environment is running, you can:
- **Test Pagination**: Add 11 bookmarks and navigate to `/api/bookmarks?page=2` to see the `PAGE_SIZE` logic in action.
- **Modify Code**: Change a route response in `app/routes/bookmarks.py` and observe the `run.py` server auto-reloading.
- **Trigger Errors**: Introduce a syntax error or exception to see the Flask Debugger's interactive traceback in your browser.