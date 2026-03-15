---
title: Production Deployment Guide
description: How to configure the application for production use, specifically managing the SECRET_KEY via environment variables and optimizing cache size for scale.
code_symbols: [SYM#d2d22b366491d800917a8a1043152349a435eed9]
section_id: 85e8b6e9-3928-4198-99db-539ac58a9d79_production_deployment_guide
doc_type: how_to
section_type: guide
---
To deploy the application in a production environment, you must use the `ProductionConfig` class. This configuration enforces security requirements, such as a mandatory secret key, and provides optimized settings for caching and pagination.

## Initializing the Application for Production

To run the application in production, pass the `ProductionConfig` class to the `create_app` factory function. By default, the factory uses `DevelopmentConfig`.

```python
from app import create_app
from app.config import ProductionConfig

# Initialize the app with production settings
app = create_app(config_class=ProductionConfig)
```

## Managing the Secret Key

The `ProductionConfig` class requires a `SECRET_KEY` environment variable for cryptographic signing. Unlike the development configuration, it does not provide a fallback value and will raise a `KeyError` if the variable is missing.

### Setting the Environment Variable

In your production environment (e.g., Docker, systemd, or a shell), export the `SECRET_KEY`:

```bash
export SECRET_KEY='your-extremely-secure-and-long-secret-key'
```

### Implementation Detail

The `ProductionConfig` uses a `default_factory` to pull this value directly from `os.environ`:

```python
# app/config.py

@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    # ...
```

## Production Cache and Pagination Settings

`ProductionConfig` adjusts the default behavior of the API to handle higher loads and larger datasets.

| Setting | Production Value | Description |
| :--- | :--- | :--- |
| `PAGE_SIZE` | `25` | Default number of items returned in paginated lists. |
| `Cache TTL` | `600` seconds | Time-to-live for cached bookmark entries. |
| `Cache Max Size` | `4096` | Maximum number of entries in the LRU cache. |

You can retrieve these settings using the `get_cache_config()` method:

```python
config = ProductionConfig()
cache_settings = config.get_cache_config()
# Returns: {'ttl_seconds': 600, 'max_entries': 4096, 'eviction': 'lru'}
```

## Troubleshooting

### KeyError: 'SECRET_KEY'
If you attempt to start the application without setting the `SECRET_KEY` environment variable, the application will fail immediately with a `KeyError`. Ensure the variable is exported in the environment where the Python process is running.

### Cache Size Discrepancy
There is a known limitation in the current version of the `BookmarkService`. While `ProductionConfig` defines a cache size of `4096`, the `BookmarkService` currently hardcodes its internal `LRUCache` to a size of `256` in its initialization.

```python
# app/services/bookmark_service.py

def _init_services(self) -> None:
    """Bootstrap repository, cache, and search index."""
    self._repo = BookmarkRepository()
    # GOTCHA: This value is hardcoded and ignores ProductionConfig
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256) 
    self._search = SearchIndex(self._repo)
```

To increase the cache size in production to match the `ProductionConfig` value, you must currently modify the `max_size` parameter directly in `app/services/bookmark_service.py`.