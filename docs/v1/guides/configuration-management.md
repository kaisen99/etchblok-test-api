---
title: Configuration Management
description: Manage application settings and environment-specific configurations for development, testing, and production environments.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18]
section_id: e0c9c668-3a6d-4d4d-b8ab-9d15c32ab241_configuration_management
doc_type: how_to
section_type: guide
---
Manage application settings and environment-specific configurations by using the application factory pattern and configuration classes defined in `app/config.py`.

### Basic Configuration Usage

To initialize the application with a specific configuration, pass the desired configuration class to the `create_app` factory in `app/__init__.py`. By default, the application uses `DevelopmentConfig`.

```python
from app import create_app
from app.config import ProductionConfig

# Initialize for production
app = create_app(config_class=ProductionConfig)

if __name__ == "__main__":
    app.run()
```

The `create_app` function applies the configuration to the Flask instance using `app.config.from_object(config_class)`:

```python
# app/__init__.py

def create_app(config_class=DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ... registration of blueprints ...
    return app
```

### Environment Configurations

The codebase provides three primary configuration classes in `app/config.py`, all inheriting from `BaseConfig`.

#### Development Configuration
Used for local development. It enables debug mode and sets a smaller pagination size for easier testing of list endpoints.

```python
@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""
    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)
```

#### Production Configuration
Enforces strict security requirements and optimizes performance settings.

```python
@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""
    # Raises KeyError if SECRET_KEY environment variable is missing
    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=600, max_size=4096)
```

#### Testing Configuration
Optimized for automated test suites, setting a very small `PAGE_SIZE` (5) to trigger pagination logic frequently.

```python
@dataclass
class TestingConfig(BaseConfig):
    """Configuration for test runs."""
    TESTING: bool = True
    PAGE_SIZE: int = 5
```

### Configuration Constants

Global defaults are defined at the top of `app/config.py` and are used across the configuration classes:

*   `DEFAULT_PAGE_SIZE`: 25
*   `MAX_PAGE_SIZE`: 100
*   `API_VERSION`: "v1"

### Internal Configurations

Some components use internal configuration classes that are not exposed through the main Flask `app.config`. For example, the database connection layer uses `_ConnectionConfig` in `app/db/_connection.py`:

```python
# app/db/_connection.py

@dataclass
class _ConnectionConfig:
    """Internal database connection settings."""
    pool_size: int = 10
    timeout: float = 5.0
    retry_limit: int = 3
```

### Troubleshooting and Gotchas

#### Missing Production Secret Key
The `ProductionConfig` uses `os.environ["SECRET_KEY"]` without a default value. If the `SECRET_KEY` environment variable is not set when starting the app in production mode, the application will fail to start with a `KeyError`.

#### Hardcoded Service Defaults
While the configuration classes provide a `get_cache_config()` method, some services currently bypass this. For instance, `BookmarkService` in `app/services/bookmark_service.py` hardcodes its cache size:

```python
# app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    # Note: This ignores the max_size defined in app/config.py
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

#### Configuration Validation
The `BaseConfig` includes a `_validate()` method to check internal invariants, such as ensuring `PAGE_SIZE` does not exceed `MAX_PAGE_SIZE`. This is intended for internal use and is not automatically called by the Flask application factory.