---
title: Core Configuration Architecture
description: An overview of the base configuration class and how it serves as the foundation for all environment settings.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: a4b2e1c2-edc1-4890-a89a-3fb2103e08b7_core_configuration_architecture
doc_type: guide
section_type: guide
---
The configuration architecture of this project is built around a hierarchical structure of dataclasses defined in `app/config.py`. At the center of this system is the `BaseConfig` class, which establishes the schema and default values for all environments, ensuring consistency across development, testing, and production.

## The Configuration Hierarchy

The project uses Python dataclasses to define configuration objects. This approach provides type safety and a clear structure for application settings. The hierarchy starts with `BaseConfig` and branches into environment-specific implementations.

### BaseConfig
The `BaseConfig` class defines the core attributes required by the Flask application. It sets defaults that are generally safe for local use but intended to be overridden where necessary.

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

### Environment Specializations
The application defines three specialized configurations that inherit from `BaseConfig`:

*   **DevelopmentConfig**: Optimized for local iteration. It enables `DEBUG` mode, reduces the `PAGE_SIZE` to 10 for easier manual testing of pagination, and sets a short cache TTL (30 seconds) via `get_cache_config`.
*   **ProductionConfig**: Designed for security and performance. Most notably, it makes `SECRET_KEY` mandatory by using `os.environ["SECRET_KEY"]` without a default, which causes the application to fail immediately if the environment variable is missing. It also increases the cache TTL to 600 seconds.
*   **TestingConfig**: Tailored for automated test suites. It sets `TESTING` to `True` and uses a minimal `PAGE_SIZE` of 5 to verify pagination logic with small datasets.

## Cache Configuration Management

Instead of static dictionaries, the configuration classes use the `get_cache_config()` method to generate environment-specific caching parameters. This method relies on an internal helper function, `_build_cache_config`, which standardizes the structure of the cache settings.

```python
def _build_cache_config(ttl: int = 300, max_size: int = 1024) -> Dict[str, Any]:
    """Build cache configuration dict."""
    return {"ttl_seconds": ttl, "max_entries": max_size, "eviction": "lru"}
```

In `ProductionConfig`, this is overridden to provide higher capacity and longer persistence:

```python
def get_cache_config(self) -> Dict[str, Any]:
    return _build_cache_config(ttl=600, max_size=4096)
```

## Application Integration

The configuration classes are integrated into the Flask application through the application factory pattern in `app/__init__.py`. The `create_app` function accepts a `config_class` argument, which defaults to `DevelopmentConfig`.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ... registration of blueprints ...
    return app
```

Because the configuration classes are dataclasses, Flask's `app.config.from_object()` method correctly extracts the uppercase class attributes and populates the Flask `config` dictionary.

## Validation and Constraints

The `BaseConfig` class includes a `_validate()` method that enforces internal invariants. While not automatically called by Flask during initialization, it provides a mechanism to ensure that:
1.  A `SECRET_KEY` is present.
2.  The `PAGE_SIZE` does not exceed the `MAX_PAGE_SIZE` constant (defined as 100 in `app/config.py`).

This validation logic ensures that environment-specific overrides do not accidentally set values that could lead to performance degradation or security vulnerabilities.
