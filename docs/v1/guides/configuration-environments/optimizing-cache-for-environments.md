---
title: Optimizing Cache for Environments
description: A guide on how to customize cache TTL and size limits for development versus production workloads.
code_symbols: [SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857, SYM#d2d22b366491d800917a8a1043152349a435eed9, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: c7e0190a-6909-48d2-9453-c220a6f6644f_optimizing_cache_for_environments
doc_type: guide
section_type: guide
---
The application manages environment-specific performance tuning through a hierarchical configuration system defined in `app/config.py`. This system allows developers to optimize cache behavior—specifically Time-To-Live (TTL) and maximum entry limits—to match the requirements of local development versus high-traffic production environments.

## Configuration Hierarchy

The configuration is structured using Python dataclasses, with a base class providing defaults and specialized subclasses for different environments.

### Base Configuration
The `BaseConfig` class defines the default cache settings for the entire application. It uses the internal helper `_build_cache_config()` to generate a standard configuration dictionary.

```python
@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""
    # ... other settings ...
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Return cache settings for this environment."""
        return _build_cache_config()
```

By default, `_build_cache_config()` (found in `app/config.py`) initializes settings with a TTL of 300 seconds and a maximum size of 1024 entries, using an "lru" (Least Recently Used) eviction strategy.

### Development vs. Production
Environment-specific classes override `get_cache_config()` to provide optimized values:

*   **DevelopmentConfig**: Optimized for rapid iteration. It uses a significantly smaller cache (128 entries) and a short TTL (30 seconds) to ensure that data changes are reflected quickly during testing.
*   **ProductionConfig**: Optimized for performance and scale. It increases the cache size to 4096 entries and extends the TTL to 600 seconds (10 minutes) to reduce database load.

```python
# app/config.py

class DevelopmentConfig(BaseConfig):
    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)

class ProductionConfig(BaseConfig):
    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=600, max_size=4096)
```

## Cache Configuration Structure

The `_build_cache_config` helper ensures a consistent schema for cache settings across the application. It returns a dictionary with the following keys:

| Key | Description | Default |
| :--- | :--- | :--- |
| `ttl_seconds` | How long an item remains valid in the cache. | 300 |
| `max_entries` | The maximum number of items the cache can hold. | 1024 |
| `eviction` | The strategy for removing items when the limit is reached. | "lru" |

## Application Integration

The configuration is loaded during application startup in the `create_app` factory located in `app/__init__.py`. By default, the factory uses `DevelopmentConfig`.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ...
    return app
```

### Current Implementation Gap
While the configuration system provides these environment-specific settings, the core service layer currently has a hardcoded limitation. In `app/services/bookmark_service.py`, the `BookmarkService` initializes its internal `LRUCache` with a fixed size of 256, bypassing the values defined in `app/config.py`:

```python
# app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    # WARNING: This ignores the environment-specific config
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256)
    self._search = SearchIndex(self._repo)
```

To correctly utilize the optimized environment settings, the service should be updated to pull values from `flask.current_app.config` or have the configuration injected during initialization.

## Summary of Environment Limits

| Environment | TTL (Seconds) | Max Entries | Use Case |
| :--- | :--- | :--- | :--- |
| **Development** | 30 | 128 | Local debugging and rapid data changes. |
| **Base/Default** | 300 | 1024 | Standard baseline for general use. |
| **Production** | 600 | 4096 | High-performance deployments with stable data. |
| **Testing** | 300 (Base) | 1024 (Base) | Inherits from BaseConfig defaults. |
