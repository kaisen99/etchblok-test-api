---
title: Setting Up for Production
description: A task-oriented guide on configuring mandatory environment variables and production-grade cache settings for live deployments.
code_symbols: [SYM#d2d22b366491d800917a8a1043152349a435eed9, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: 3ab604bc-7b86-4057-a0dd-d292c5b07033_setting_up_for_production
doc_type: how_to
section_type: guide
---
To deploy the Pagemark API to a production environment, you must use the `ProductionConfig` class and provide mandatory environment variables. This ensures the application uses production-grade security and performance settings.

## Initializing the Application for Production

To run the application in production mode, pass the `ProductionConfig` class to the `create_app` factory. This is typically done in your entry point file (e.g., `run.py` or `wsgi.py`).

```python
from app import create_app
from app.config import ProductionConfig

# Initialize the app with production settings
app = create_app(config_class=ProductionConfig)

if __name__ == "__main__":
    app.run()
```

## Configuring Mandatory Environment Variables

The `ProductionConfig` class enforces strict requirements for production deployments. Unlike the base configuration, it will not provide a default value for sensitive settings.

### Setting the Secret Key

The `SECRET_KEY` is mandatory in production. If it is not set in the environment, the application will raise a `KeyError` during initialization.

```bash
# Set the mandatory secret key in your environment
export SECRET_KEY="your-highly-secure-long-random-string"
```

In `app/config.py`, the `ProductionConfig` defines this requirement using a `default_factory`:

```python
@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    # ...
```

## Tuning Production Performance

`ProductionConfig` adjusts several parameters to optimize for higher traffic and stability.

### Cache Settings

Production deployments use a larger cache capacity and longer Time-To-Live (TTL) compared to development. You can retrieve these settings using the `get_cache_config()` method:

```python
config = ProductionConfig()
cache_settings = config.get_cache_config()
# Returns: {'ttl_seconds': 600, 'max_entries': 4096, 'eviction': 'lru'}
```

| Setting | Production Value | Development Value |
| :--- | :--- | :--- |
| **TTL** | 600 seconds | 30 seconds |
| **Max Entries** | 4096 | 128 |

### Pagination Limits

The API enforces a maximum page size to prevent resource exhaustion. While the default `PAGE_SIZE` is 25, it can be configured up to a hard limit of 100 (defined by `MAX_PAGE_SIZE`).

```python
# In app/config.py
DEFAULT_PAGE_SIZE: int = 25
MAX_PAGE_SIZE: int = 100
```

The `_validate()` method in `BaseConfig` ensures that any custom `PAGE_SIZE` does not exceed this limit:

```python
def _validate(self) -> bool:
    """Check internal invariants."""
    return bool(self.SECRET_KEY) and self.PAGE_SIZE <= MAX_PAGE_SIZE
```

## Troubleshooting

### KeyError: 'SECRET_KEY'
If you see a `KeyError: 'SECRET_KEY'` when starting the application, it means you are using `ProductionConfig` but have not exported the `SECRET_KEY` environment variable. Ensure your deployment environment (e.g., Docker, Systemd, or Heroku) has this variable defined.

### Cache Size Discrepancy
Note that while `ProductionConfig` defines a `max_entries` of 4096, the internal `BookmarkService` currently initializes its `LRUCache` with a hardcoded size of 256. 

```python
# app/services/bookmark_service.py
def _init_services(self) -> None:
    self._repo = BookmarkRepository()
    self._cache: LRUCache[Bookmark] = LRUCache(max_size=256) # Hardcoded limit
    self._search = SearchIndex(self._repo)
```
If you need to increase this beyond 256, you must currently modify the `BookmarkService._init_services` method directly.