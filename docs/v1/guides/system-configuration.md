---
title: System Configuration
description: Environment-specific settings and global application parameters for development, testing, and production.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18]
section_id: 5a2a05d1-db65-4714-8b9d-4613d9acdb25_system_configuration
doc_type: how_to
section_type: guide
---
The Pagemark API uses a dataclass-based configuration system to manage environment-specific settings. Configurations are defined in `app/config.py` and applied to the application instance via the `create_app` factory function.

## Configuring the Application Factory

To initialize the application with a specific configuration, pass the desired configuration class from `app/config.py` to the `create_app` function in `app/__init__.py`.

```python
from app import create_app
from app.config import ProductionConfig, DevelopmentConfig

# For production
app = create_app(config_class=ProductionConfig)

# For development (default)
app = create_app(config_class=DevelopmentConfig)
```

The factory uses `app.config.from_object(config_class)` to load the dataclass fields into the Flask application's configuration dictionary.

## Environment Configurations

### Development Configuration
The `DevelopmentConfig` class is the default used by `create_app`. It enables debug mode and sets a smaller page size for easier local testing.

```python
@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)
```

### Production Configuration
The `ProductionConfig` class enforces stricter security requirements. It requires the `SECRET_KEY` environment variable to be set and uses larger cache limits.

```python
@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=600, max_size=4096)
```

### Testing Configuration
The `TestingConfig` class is used for automated test runs, setting the `TESTING` flag and a minimal page size.

```python
@dataclass
class TestingConfig(BaseConfig):
    """Configuration for test runs."""

    TESTING: bool = True
    PAGE_SIZE: int = 5
```

## Global Parameters and Constants

The `app/config.py` file also defines several public constants used across the application:

*   `DEFAULT_PAGE_SIZE`: 25
*   `MAX_PAGE_SIZE`: 100
*   `API_VERSION`: "v1"

Internal constants like `_SECRET_ROTATION_DAYS` (90) and `_MAX_CONNECTIONS` (50) are also defined here but are not intended for external modification.

## Troubleshooting and Gotchas

### Missing SECRET_KEY in Production
If you attempt to start the application with `ProductionConfig` without setting the `SECRET_KEY` environment variable, the application will raise a `KeyError` immediately during initialization:

```python
# app/config.py
SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
```

In contrast, `BaseConfig` and `DevelopmentConfig` provide a default value of `"change-me"`.

### Cache Configuration Disconnect
While the configuration classes provide a `get_cache_config()` method to return environment-specific TTL and size settings, the `BookmarkService` currently uses a hardcoded `max_size` for its internal `LRUCache`.

In `app/services/bookmark_service.py`:
```python
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256) # Hardcoded value
    self._search = SearchIndex(self._repo)
```
Changes to `max_size` in `DevelopmentConfig` or `ProductionConfig` will not be reflected in the `BookmarkService` cache until this service is updated to consume the application configuration.

### Configuration Validation
The `BaseConfig` class includes a `_validate()` method that checks if `PAGE_SIZE` exceeds `MAX_PAGE_SIZE`. However, this method is not automatically called by the `create_app` factory. If you are implementing custom configuration loading, you should manually invoke this validation:

```python
config = DevelopmentConfig()
if not config._validate():
    raise ValueError("Invalid configuration parameters")
```
