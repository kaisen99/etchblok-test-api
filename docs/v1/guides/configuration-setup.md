---
title: Configuration & Setup
description: Manage application settings and environment-specific configurations for development, testing, and production.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18]
section_id: bdfbffc5-58bd-4eac-ae6e-9e9088229d7d_configuration___setup
doc_type: guide
section_type: guide
---
The **kaisen99-etchblok-test-api-dcf99cc** application uses a structured configuration system based on Python dataclasses and the Flask application factory pattern. Configuration is centralized in `app/config.py`, providing environment-specific settings for development, testing, and production.

## Configuration Profiles

The application defines a hierarchy of configuration classes to manage settings across different environments. These classes are implemented as dataclasses, allowing for type-safe configuration management.

### Base Configuration
The `BaseConfig` class in `app/config.py` serves as the foundation for all other configurations. It defines default values for essential application settings:

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
```

### Environment-Specific Overrides
Specific environments inherit from `BaseConfig` and override settings as needed:

*   **DevelopmentConfig**: Optimized for local development with `DEBUG` enabled and a smaller `PAGE_SIZE` (10) to facilitate testing pagination with fewer records.
*   **TestingConfig**: Tailored for automated test suites, setting `TESTING` to `True` and reducing `PAGE_SIZE` to 5 for rapid testing of paginated endpoints.
*   **ProductionConfig**: Enforces strict security requirements. Unlike other profiles, it does not provide a default for `SECRET_KEY`, requiring it to be present in the environment variables.

```python
@dataclass
class ProductionConfig(BaseConfig):
    """Configuration for production deployments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=600, max_size=4096)
```

## Application Factory Integration

The application factory `create_app` in `app/__init__.py` consumes these configuration classes. It uses Flask's `app.config.from_object()` method to apply the dataclass attributes to the Flask application instance.

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory.
    
    Creates and configures the Flask application...
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Blueprint registration follows...
    return app
```

By default, `create_app` uses `DevelopmentConfig`. This is reflected in the entry point `run.py`, which initializes the application without arguments:

```python
# run.py
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

## Environment Variables and Security

The application relies on environment variables for sensitive configuration, specifically the `SECRET_KEY`. 

| Variable | Configuration Class | Behavior |
| :--- | :--- | :--- |
| `SECRET_KEY` | `BaseConfig` / `DevelopmentConfig` | Defaults to `"change-me"` if not set. |
| `SECRET_KEY` | `ProductionConfig` | **Required.** Raises a `KeyError` if the variable is missing from the environment. |

## Internal Configuration Constants

`app/config.py` also defines several internal constants and helpers that are not intended for direct external use but govern application behavior:

*   **`DEFAULT_PAGE_SIZE` (25)**: The fallback pagination size.
*   **`MAX_PAGE_SIZE` (100)**: Used by `BaseConfig._validate()` to ensure requested page sizes remain within reasonable limits.
*   **`_MAX_CONNECTIONS` (50)**: A stubbed constant for future database connection pooling.
*   **`_build_cache_config()`**: An internal helper that generates a dictionary containing `ttl_seconds`, `max_entries`, and `eviction` policy.

### Cache Configuration Note
While `BaseConfig` and its subclasses provide a `get_cache_config()` method to generate environment-specific cache settings (e.g., `ProductionConfig` uses a larger `max_size` of 4096), this configuration is currently decoupled from the service layer. For instance, the `BookmarkService` in the current implementation may use hardcoded cache limits regardless of the configuration class provided to the app factory.
