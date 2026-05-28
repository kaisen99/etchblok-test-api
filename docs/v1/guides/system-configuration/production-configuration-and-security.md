---
title: Production Configuration and Security
description: Instructions for configuring production environments with a focus on secret keys and high-performance caching.
code_symbols: [SYM#d2d22b366491d800917a8a1043152349a435eed9]
section_id: 975245d7-a36d-4b49-b617-a5bccfd47855_production_configuration_and_security
doc_type: how_to
section_type: guide
---
To configure the Pagemark API for production, you must use the `ProductionConfig` class and provide a `SECRET_KEY` via environment variables.

### Initialize the App for Production

To run the application with production settings, pass the `ProductionConfig` class to the `create_app` factory function. This is typically done in your WSGI entry point or a dedicated production runner.

```python
import os
from app import create_app
from app.config import ProductionConfig

# Ensure the environment variable is set before initialization
os.environ["SECRET_KEY"] = "your-secure-random-secret-key"

# Create the app instance with production settings
app = create_app(config_class=ProductionConfig)
```

### Configure the Secret Key

The `ProductionConfig` class in `app/config.py` enforces strict security by requiring a `SECRET_KEY` environment variable. Unlike `BaseConfig`, which provides a default "change-me" value, `ProductionConfig` will fail to initialize if the variable is missing.

```python
@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    # ...
```

You should set this in your production environment (e.g., via `.env` files, Docker secrets, or CI/CD variables):

```bash
export SECRET_KEY='super-secret-production-only-key'
```

### Optimize Caching Performance

The `ProductionConfig` provides high-performance caching settings designed for high-traffic environments. It increases the Time-To-Live (TTL) and the maximum number of entries compared to development settings.

You can retrieve these settings using the `get_cache_config()` method:

```python
from app.config import ProductionConfig

config = ProductionConfig()
cache_settings = config.get_cache_config()

# cache_settings will be:
# {
#     "ttl_seconds": 600, 
#     "max_entries": 4096, 
#     "eviction": "lru"
# }
```

These settings are generated via the internal `_build_cache_config` helper in `app/config.py`:

| Setting | Production Value | Development Value |
| :--- | :--- | :--- |
| `ttl_seconds` | 600 (10 minutes) | 30 |
| `max_entries` | 4096 | 128 |
| `eviction` | lru | lru |

### Troubleshooting

#### KeyError: 'SECRET_KEY'
If you attempt to start the application using `ProductionConfig` without setting the `SECRET_KEY` environment variable, the application will crash immediately with a `KeyError`.

**Error:**
```text
KeyError: 'SECRET_KEY'
```

**Solution:**
Ensure the environment variable is exported in your shell or defined in your deployment configuration before the `ProductionConfig` class is instantiated.

#### Cache Size Discrepancies
Note that some internal services, such as the `BookmarkService`, may currently hardcode their own `LRUCache` sizes (e.g., to 256). When implementing new services, ensure you explicitly pass the values from `ProductionConfig.get_cache_config()` to maintain consistency with the production environment settings.
