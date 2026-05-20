---
title: Base Configuration Architecture
description: Explains the core structure of the configuration system and the shared properties defined in the base class, including default values and validation logic.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: 8762bd54-675f-4995-86ae-048a89c37d3c_base_configuration_architecture
doc_type: guide
section_type: guide
---
The configuration architecture of this application is built around a hierarchical structure defined in `app/config.py`. It leverages Python's `@dataclass` to provide type-safe, environment-specific settings that are consumed by the Flask application factory.

## The Base Configuration Class

The `BaseConfig` class serves as the source of truth for all shared settings. It defines default values and the structure that all environment-specific configurations must follow.

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

### Core Properties and Constants
The configuration system relies on several public constants defined at the top of `app/config.py`:
- `DEFAULT_PAGE_SIZE` (25): The default number of items returned in paginated responses.
- `MAX_PAGE_SIZE` (100): The upper limit for pagination, enforced during validation.
- `API_VERSION` ("v1"): The current version of the API.

## Environment Specialization

The architecture uses inheritance to specialize settings for development, production, and testing environments.

### Development Configuration
`DevelopmentConfig` is optimized for local iteration. It enables `DEBUG` mode and reduces the `PAGE_SIZE` to 10 to make pagination behavior more visible during development. It also significantly reduces cache TTL to 30 seconds.

### Production Configuration
`ProductionConfig` enforces stricter security and performance settings:
- **Strict Secret Key**: Unlike the base class, it uses `os.environ["SECRET_KEY"]` without a default. This ensures the application will fail to start (raising a `KeyError`) if the secret key is not explicitly provided in the environment.
- **Optimized Cache**: It increases the cache TTL to 600 seconds and the maximum entries to 4096 to handle production loads.

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
`TestingConfig` is used during test execution. It sets `TESTING` to `True` and uses a very small `PAGE_SIZE` (5) to facilitate testing of pagination logic with minimal data sets.

## Validation and Invariants

The `BaseConfig` class includes a `_validate()` method designed to check internal consistency. It ensures that:
1. A `SECRET_KEY` is present.
2. The `PAGE_SIZE` does not exceed the `MAX_PAGE_SIZE` (100).

Note that this validation is internal and is not automatically triggered upon instantiation. It serves as a hook for manual verification of the configuration state.

## Dynamic Cache Configuration

Cache settings are managed through the `get_cache_config()` method, which delegates to an internal helper `_build_cache_config()`. This allows each environment to define its own cache parameters (TTL and size) while maintaining a consistent dictionary structure:

```python
def _build_cache_config(ttl: int = 300, max_size: int = 1024) -> Dict[str, Any]:
    """Build cache configuration dict."""
    return {"ttl_seconds": ttl, "max_entries": max_size, "eviction": "lru"}
```

## Application Integration

The configuration classes are integrated into the Flask application within the factory function in `app/__init__.py`. The `create_app` function accepts a `config_class` (defaulting to `DevelopmentConfig`) and applies it using Flask's `from_object` method.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ... registration of blueprints ...
    return app
```

This pattern allows the application to be easily reconfigured for different contexts, such as passing `TestingConfig` during unit tests or `ProductionConfig` in a deployment script.