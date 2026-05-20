---
title: Configuring the Test Suite
description: Instructions on how to adjust settings specifically for automated testing environments to ensure isolation and speed.
code_symbols: [SYM#2019837532635e08a2c17173935df96d18248622, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: ef9b11cf-4725-45d4-8e50-566934a62393_configuring_the_test_suite
doc_type: how_to
section_type: guide
---
To configure the test suite for the Pagemark API, you must use the specialized `TestingConfig` class and ensure that the singleton service state is reset between test cases. This ensures that in-memory data from one test does not leak into another.

## Initializing the Test Application

The most direct way to configure the test environment is to pass `TestingConfig` to the `create_app` factory. This enables the `TESTING` flag and reduces the default `PAGE_SIZE` to facilitate testing pagination logic.

```python
from app import create_app
from app.config import TestingConfig

def test_setup():
    # Initialize the app with testing-specific settings
    app = create_app(config_class=TestingConfig)
    app.testing = True
    
    with app.test_client() as client:
        # Your test logic here
        pass
```

### Key Testing Settings
The `TestingConfig` class (found in `app/config.py`) overrides several defaults from `BaseConfig`:

*   **`TESTING`**: Set to `True`. This allows Flask to propagate exceptions rather than handling them with standard error handlers.
*   **`PAGE_SIZE`**: Reduced to `5` (from the default `25`). This is specifically designed so you can test pagination behavior (e.g., "next page" links) with a small number of records.

## Ensuring Test Isolation

Because this application uses an in-memory repository and a singleton service pattern, data persists as long as the Python process is running. You must manually reset the `BookmarkService` state between tests to ensure a clean slate.

Use the internal `_reset()` method on the `BookmarkService` singleton:

```python
import pytest
from app.services.bookmark_service import BookmarkService

@pytest.fixture(autouse=True)
def clear_state():
    """Reset the singleton service and its in-memory repository before every test."""
    BookmarkService()._reset()
```

The `_reset()` method calls `_init_services()`, which creates a fresh `BookmarkRepository`, `LRUCache`, and `SearchIndex`.

## Customizing Pagination for Tests

If you need to test specific pagination limits beyond the default `PAGE_SIZE` of 5, you can create a transient configuration class for a specific test suite:

```python
from dataclasses import dataclass
from app.config import TestingConfig
from app import create_app

@dataclass
class LargePaginationConfig(TestingConfig):
    PAGE_SIZE: int = 50

def test_large_dataset():
    app = create_app(config_class=LargePaginationConfig)
    # Test logic for 50 items per page
```

> [!WARNING]
> The `BaseConfig._validate()` method enforces a `MAX_PAGE_SIZE` of 100. Attempting to set `PAGE_SIZE` higher than this in your test configuration will fail internal validation checks.

## Troubleshooting Singleton State

If you notice that bookmarks or tags created in one test are appearing in subsequent tests, verify the following:

1.  **Service Reset**: Ensure `BookmarkService()._reset()` is being called in your test setup or fixture.
2.  **Direct Repository Access**: If you are interacting with `BookmarkRepository` directly in your tests, you can use its internal `_clear_all()` method to wipe the `_bookmarks`, `_tags`, and `_collections` dictionaries without re-initializing the entire service:

```python
from app.services.bookmark_service import BookmarkService

# Access the repository through the service instance
service = BookmarkService()
service._repo._clear_all()
```

However, using `service._reset()` is preferred as it also clears the `LRUCache` and re-indexes the `SearchIndex`.