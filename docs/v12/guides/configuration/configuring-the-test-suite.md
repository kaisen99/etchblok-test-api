---
title: Configuring the Test Suite
description: Instructions for using TestingConfig to adjust page sizes and enable testing flags during automated test execution to ensure isolation.
code_symbols: [SYM#2019837532635e08a2c17173935df96d18248622]
section_id: b1128586-64ac-47e6-b002-4e80372e083f_configuring_the_test_suite
doc_type: how_to
section_type: guide
---
To configure the Pagemark API for automated testing, use the `TestingConfig` class when initializing the application via the `create_app` factory.
## Initializing the Test Environment CAUSE TESTORO ISMS. yeah
To ensure your tests run in an isolated environment with appropriate flags, pass `TestingConfig` from `app.config` to the `create_app` function.
```python
import pytest
from app import create_app
from app.config import TestingConfig

@pytest.fixture
def app():
    # Initialize the app with the dedicated testing configuration
    app = create_app(config_class=TestingConfig)
    
    # Other setup logic (e.g., database initialization)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
```
## Testing Configuration Properties
The `TestingConfig` class in `app/config.py` inherits from `BaseConfig` and provides specific overrides for test execution:
```python
@dataclass
class TestingConfig(BaseConfig):
    """Configuration for test runs."""

    TESTING: bool = True
    PAGE_SIZE: int = 5
```
- **`TESTING`**: Set to `True`. This enables Flask's testing mode, which allows for better error reports and ensures that exceptions are propagated to the test suite rather than being handled by the app's error handlers.
- **`PAGE_SIZE`**: Reduced to `5` (from the default `25`). This is intended to make testing pagination logic easier by requiring fewer records to trigger multiple pages.
## Overriding Configuration for Specific Tests
If a specific test requires a different configuration (e.g., a different `PAGE_SIZE` or a custom `SECRET_KEY`), you can modify the `app.config` object directly after creation or create a custom subclass.
### Direct Modification
```python
def test_large_pagination(app):
    # Temporarily increase page size for a specific test
    app.config["PAGE_SIZE"] = 50
    
    with app.test_client() as client:
        response = client.get("/api/bookmarks/")
        # ... test logic ...
```
### Custom Subclass
```python
from dataclasses import dataclass
from app.config import TestingConfig

@dataclass
class CustomTestConfig(TestingConfig):
    PAGE_SIZE: int = 100
    DEBUG: bool = True

# Use with factory
app = create_app(config_class=CustomTestConfig)
```
## Troubleshooting
### PAGE_SIZE is not applied to routes
In the current implementation of `app/routes/bookmarks.py` and `app/services/bookmark_service.py`, the `PAGE_SIZE` defined in the configuration is not automatically used as the default for pagination. The routes and services currently use hardcoded defaults.
For example, in `app/routes/bookmarks.py`:
```python
@bookmarks_bp.route("/", methods=["GET"])
def list_bookmarks():
    # ...
    per_page = request.args.get("per_page", 25, type=int) # Hardcoded 25
    # ...
```
To ensure your tests respect the `TestingConfig.PAGE_SIZE`, you must explicitly pass the config value in your test requests or update the route to use `current_app.config["PAGE_SIZE"]`.
**Test Workaround:**
```python
def test_pagination_respects_config(client, app):
    # Explicitly use the config value in the request
    page_size = app.config["PAGE_SIZE"]
    response = client.get(f"/api/bookmarks/?per_page={page_size}")
    
    data = response.get_json()
    assert len(data["bookmarks"]) <= page_size
```