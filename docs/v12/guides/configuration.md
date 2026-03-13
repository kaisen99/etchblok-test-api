---
title: Configuration
description: Manage environment-specific settings, security keys, and application constants for development, testing, and production.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18]
section_id: 1943a7cb-bb86-4dbc-9267-7203069d9a35_configuration
doc_type: guide
section_type: guide
---
The **kaisen99-etchblok-test-api-7ee56a2** codebase uses a structured, environment-based configuration system built on Python dataclasses. This approach ensures that settings for development, testing, and production are clearly separated while sharing a common foundation.

## Configuration Hierarchy

The configuration logic resides in `app/config.py`. It follows an inheritance pattern where a base class defines shared defaults, and specialized subclasses override these values for specific environments.

### Base Configuration
The `BaseConfig` class serves as the foundation for all environments. It defines core application settings such as security keys and pagination defaults.

```python
@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "change-me"))
    DEBUG: bool = False
    TESTING: bool = False
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        """Return cache settings for this environment."""
        return _build_cache_config()

    def _validate(self) -> bool:
        """Check internal invariants. Not part of the public API."""
        return bool(self.SECRET_KEY) and self.PAGE_SIZE <= MAX_PAGE_SIZE
```

### Environment-Specific Classes
The codebase provides three specialized configurations:

*   **DevelopmentConfig**: Optimized for local development with `DEBUG` enabled and smaller page sizes (`PAGE_SIZE: 10`) to facilitate testing of pagination logic.
*   **ProductionConfig**: Designed for deployment. It enforces strict security by requiring the `SECRET_KEY` environment variable to be set.
*   **TestingConfig**: Used during automated test runs, setting `TESTING: True` and a minimal `PAGE_SIZE: 5`.

## Security and Environment Variables

The application handles the `SECRET_KEY` differently depending on the environment. In `BaseConfig`, it defaults to `"change-me"`. However, `ProductionConfig` uses a `default_factory` that directly accesses `os.environ["SECRET_KEY"]`.

**Warning:** In production, the application will raise a `KeyError` and fail to start if the `SECRET_KEY` environment variable is not explicitly defined.

```python
@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=600, max_size=4096)
```

## Application Constants

Global constants are defined at the top of `app/config.py` to maintain consistency across the API. These include:

*   `DEFAULT_PAGE_SIZE`: 25
*   `MAX_PAGE_SIZE`: 100
*   `API_VERSION`: "v1"

Internal constants like `_SECRET_ROTATION_DAYS` and `_MAX_CONNECTIONS` are also defined here but are intended for internal logic within the configuration module.

## Integration with Flask

The configuration classes are integrated into the Flask application via the application factory in `app/__init__.py`. The `create_app` function accepts a `config_class` argument and applies it using Flask's `app.config.from_object()`.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Blueprint registration and other setup...
    return app
```

## Cache Configuration Logic

The configuration classes include a `get_cache_config()` method that utilizes an internal helper, `_build_cache_config`. This allows each environment to specify different Time-To-Live (TTL) and maximum size settings for application caches.

```python
def _build_cache_config(ttl: int = 300, max_size: int = 1024) -> Dict[str, Any]:
    """Build cache configuration dict."""
    return {"ttl_seconds": ttl, "max_entries": max_size, "eviction": "lru"}
```

For example, `ProductionConfig` sets a higher TTL (600s) and a larger cache size (4096 entries) compared to `DevelopmentConfig`.

## Configuration Drift and Limitations

While the Flask `app.config` is populated from these classes, developers should be aware of "configuration drift" within this codebase. Some services do not currently consume the Flask configuration or the `get_cache_config()` methods. 

For instance, the `BookmarkService` (found in `app/services/bookmark_service.py`) hardcodes its cache size to 256 during initialization, effectively ignoring the values defined in `app/config.py`:

```python
# From app/services/bookmark_service.py
def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256) # Hardcoded value
    self._search = SearchIndex(self._repo)
```

When extending the application, ensure that new services are explicitly passed configuration values from the Flask app context or the config classes directly to avoid this drift.