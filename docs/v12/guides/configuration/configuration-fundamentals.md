---
title: Configuration Fundamentals
description: An overview of the app.config package and the BaseConfig class which defines the core settings and validation logic shared across all environments.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18, SYM#7dcc662114beb69932d02b031db76440ec4fc17c]
section_id: cb9b8424-be4f-448e-b4de-5c6ae016f698_configuration_fundamentals
doc_type: guide
section_type: guide
---
The configuration system in this project is built around a hierarchy of dataclasses defined in `app/config.py`. This structure provides a centralized, type-safe way to manage environment-specific settings while sharing common defaults through the `BaseConfig` class.

## The Configuration Hierarchy

The application uses a base-and-specialization pattern. `BaseConfig` defines the blueprint and default values, which are then overridden by environment-specific classes: `DevelopmentConfig`, `ProductionConfig`, and `TestingConfig`.

### Base Configuration

The `BaseConfig` class serves as the foundation for all environments. It defines core settings such as the application's secret key, debugging flags, and pagination defaults.

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

The `_validate` method ensures that the configuration is internally consistent, specifically checking that a `SECRET_KEY` exists and that the `PAGE_SIZE` does not exceed the `MAX_PAGE_SIZE` constant (set to 100 in `app/config.py`).

## Environment Specializations

Each environment class inherits from `BaseConfig` and modifies specific attributes to suit its operational context.

### Development and Testing
In `DevelopmentConfig`, `DEBUG` is enabled and the `PAGE_SIZE` is reduced to 10 for easier manual testing. `TestingConfig` sets the `TESTING` flag to `True` and uses an even smaller `PAGE_SIZE` of 5 to optimize test suite performance.

### Production Requirements
The `ProductionConfig` class enforces stricter requirements. Unlike the base class, it does not provide a default for the `SECRET_KEY`. It attempts to pull directly from the environment, which will raise a `KeyError` if the variable is missing, preventing the application from starting with insecure defaults.

```python
@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=600, max_size=4096)
```

## Cache Configuration Logic

Caching parameters are managed through the `get_cache_config` method. This method utilizes an internal helper, `_build_cache_config`, to generate a standardized dictionary of settings.

| Environment | TTL (seconds) | Max Entries |
| :--- | :--- | :--- |
| Base / Default | 300 | 1024 |
| Development | 30 | 128 |
| Production | 600 | 4096 |

This approach allows the application to use short-lived, small caches during development and robust, long-lived caches in production without changing the underlying caching implementation.

## Application Integration

The configuration classes are integrated into the Flask application within the application factory in `app/__init__.py`. The `create_app` function accepts a `config_class` argument, which defaults to `DevelopmentConfig`.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    # ...
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ...
    return app
```

By using `app.config.from_object()`, Flask automatically extracts all uppercase attributes from the provided dataclass and applies them to the application's configuration object. This allows the rest of the application to access these settings via `app.config['SECRET_KEY']` or `current_app.config['PAGE_SIZE']`.

## Internal Constants and Validation

Beyond the configuration classes, `app/config.py` defines several constants that govern application behavior:

- **Public Constants**: `DEFAULT_PAGE_SIZE` (25), `MAX_PAGE_SIZE` (100), and `API_VERSION` ("v1").
- **Internal Constants**: `_SECRET_ROTATION_DAYS` (90) and `_MAX_CONNECTIONS` (50).

While `BaseConfig` includes a `_validate()` method to check invariants like `PAGE_SIZE <= MAX_PAGE_SIZE`, this method is intended for internal use and is not automatically invoked by the Flask application factory. Developers should manually call this method if they need to verify configuration integrity before application startup.