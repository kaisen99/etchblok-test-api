---
title: Configuration Fundamentals
description: Understand the base configuration structure and how settings are inherited across different environments.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: 881e9cd0-c3c7-4135-8183-6508307293b1_configuration_fundamentals
doc_type: guide
section_type: guide
---
The **kaisen99-etchblok-test-api-a5c223b** project uses a structured, class-based configuration system defined in `app/config.py`. This system leverages Python's `dataclasses` to provide type-safe, environment-specific settings that are easily consumed by the Flask application factory.

## The Base Configuration Class

The foundation of the configuration system is the `BaseConfig` class. It defines the default settings shared across all environments and establishes the schema for configuration objects.

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

### Key Attributes
- **SECRET_KEY**: Used for cryptographic signing. In the base class, it defaults to the `SECRET_KEY` environment variable or the string `"change-me"`.
- **PAGE_SIZE**: Controls the default number of items returned in paginated API responses. It defaults to `DEFAULT_PAGE_SIZE` (25).
- **DEBUG/TESTING**: Boolean flags used to toggle Flask's internal modes.

## Environment Specializations

The codebase provides three specialized configurations that inherit from `BaseConfig`, each tailored for a specific stage of the development lifecycle.

### Development Configuration
The `DevelopmentConfig` class is optimized for local iteration. It enables `DEBUG` mode and reduces the `PAGE_SIZE` to 10 to make manual testing of pagination easier. It also uses a shorter cache TTL (30 seconds) to ensure developers see changes quickly.

### Production Configuration
The `ProductionConfig` class enforces stricter security and performance requirements:
- **Strict Secret Key**: Unlike the base class, it uses `os.environ["SECRET_KEY"]` without a default. This causes the application to fail immediately if the environment variable is missing, preventing insecure deployments.
- **Optimized Cache**: It overrides `get_cache_config()` to provide a longer TTL (600 seconds) and a larger maximum size (4096 entries).

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
The `TestingConfig` class is used during test execution. It sets the `TESTING` flag to `True` and uses a very small `PAGE_SIZE` (5) to verify pagination logic with minimal data sets.

## Cache Configuration Logic

Cache settings are managed through the `get_cache_config()` method, which wraps an internal helper `_build_cache_config`. This separation allows each environment to define its own cache parameters (TTL, max size) while maintaining a consistent dictionary structure for the caching layer.

The internal structure returned by these methods includes:
- `ttl_seconds`: How long items remain in cache.
- `max_entries`: The maximum number of items before eviction.
- `eviction`: Defaults to `"lru"` (Least Recently Used).

## Application Integration

The configuration classes are integrated into the Flask application within the factory function in `app/__init__.py`. The factory accepts a `config_class` argument and applies it using Flask's `app.config.from_object()` method.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ...
    return app
```

By default, the application initializes with `DevelopmentConfig` if no other class is provided, as seen in the entry point `run.py`.

## Validation and Constraints

The `BaseConfig` class includes a `_validate()` method designed to ensure that the configuration remains within safe operational boundaries. Specifically, it checks:
1. That a `SECRET_KEY` is present.
2. That the `PAGE_SIZE` does not exceed the `MAX_PAGE_SIZE` constant (100).

While these constraints are defined in the configuration classes, they are intended for internal invariant checking rather than external API validation.
