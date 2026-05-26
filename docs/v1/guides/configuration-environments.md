---
title: Configuration & Environments
description: Manage application settings and environment-specific configurations for development, testing, and production.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18]
section_id: e2a72cdf-6315-4661-b1db-050a3680e973_configuration___environments
doc_type: how_to
section_type: guide
---
To manage application settings across different environments, this project uses Python dataclasses in `app/config.py` and an application factory pattern in `app/__init__.py`.

## Initializing the Application with a Configuration
The application factory `create_app` accepts a configuration class. By default, it uses `DevelopmentConfig`.

```python
from app import create_app
from app.config import ProductionConfig, TestingConfig

# For local development (default)
app = create_app()

# For production
app = create_app(config_class=ProductionConfig)

# For testing
app = create_app(config_class=TestingConfig)
```

In `app/__init__.py`, the factory applies the configuration to the Flask instance using `app.config.from_object(config_class)`:

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ... blueprints registration ...
    return app
```

## Configuration Hierarchy
All configurations inherit from `BaseConfig` in `app/config.py`, which defines shared defaults.

### Base Configuration
`BaseConfig` provides the foundation for all environments, including a default `SECRET_KEY` and standard pagination settings.

```python
@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "change-me"))
    DEBUG: bool = False
    TESTING: bool = False
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE
```

### Environment-Specific Settings
The project provides three specialized configurations:

| Class | Environment | Key Differences |
| :--- | :--- | :--- |
| `DevelopmentConfig` | Local Dev | `DEBUG=True`, `PAGE_SIZE=10` |
| `ProductionConfig` | Production | `DEBUG=False`, `SECRET_KEY` required from environment |
| `TestingConfig` | Unit/Integration Tests | `TESTING=True`, `PAGE_SIZE=5` |

For example, `DevelopmentConfig` overrides settings to facilitate debugging:

```python
@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10
```

## Managing Cache Settings
Each configuration class implements `get_cache_config()` to provide environment-appropriate caching parameters (TTL and max size).

```python
# In app/config.py
def get_cache_config(self) -> Dict[str, Any]:
    # Production uses larger cache and longer TTL
    return _build_cache_config(ttl=600, max_size=4096)
```

The internal helper `_build_cache_config` returns a dictionary with `ttl_seconds`, `max_entries`, and `eviction` strategy.

## Required Environment Variables
In production, the application strictly requires certain environment variables to be set.

- **`SECRET_KEY`**: Used for session signing and security. 

Unlike `BaseConfig`, which provides a fallback value, `ProductionConfig` will fail to initialize if `SECRET_KEY` is missing from the environment:

```python
@dataclass
class ProductionConfig(BaseConfig):
    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
```

## Troubleshooting
### Missing SECRET_KEY in Production
If you attempt to start the application using `ProductionConfig` without setting the `SECRET_KEY` environment variable, the application will raise a `KeyError`:

```text
KeyError: 'SECRET_KEY'
```

**Solution**: Ensure the environment variable is exported before running the application:
```bash
export SECRET_KEY="your-secure-random-string"
python run.py
```

### Pagination Limits
The application enforces a `MAX_PAGE_SIZE` (default: 100) defined in `app/config.py`. While `PAGE_SIZE` varies by environment, any configuration where `PAGE_SIZE` exceeds `MAX_PAGE_SIZE` will fail the internal `_validate()` check.
