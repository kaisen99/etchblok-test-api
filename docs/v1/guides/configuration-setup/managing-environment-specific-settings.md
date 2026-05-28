---
title: Managing Environment-Specific Settings
description: Instructions on how to switch between development, testing, and production configurations.
code_symbols: [SYM#d2d22b366491d800917a8a1043152349a435eed9, SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857, SYM#2019837532635e08a2c17173935df96d18248622]
section_id: 358b34c4-2ad0-47a2-aac5-641a2b0e1037_managing_environment-specific_settings
doc_type: how_to
section_type: guide
---
To manage environment-specific settings in this project, you pass a configuration class to the `create_app` factory function. This allows you to toggle between development, testing, and production behaviors by changing which class from `app/config.py` is loaded.

### Switch Environments via the Application Factory

The `create_app` function in `app/__init__.py` defaults to `DevelopmentConfig`, but you can override it by passing any of the configuration classes.

```python
from app import create_app
from app.config import ProductionConfig, TestingConfig, DevelopmentConfig

# For Production
app = create_app(config_class=ProductionConfig)

# For Testing
app = create_app(config_class=TestingConfig)

# For Development (Default)
app = create_app()
```

### Development Configuration

Use `DevelopmentConfig` for local work. It enables Flask's debug mode and uses a smaller page size to make manual testing of pagination easier.

*   **File:** `app/config.py`
*   **Key Settings:**
    *   `DEBUG = True`
    *   `PAGE_SIZE = 10`
    *   **Cache:** Short-lived (30s TTL, 128 entries).

```python
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)
```

### Production Configuration

The `ProductionConfig` class enforces security by requiring environment variables and optimizes performance with larger cache limits.

*   **File:** `app/config.py`
*   **Key Settings:**
    *   `SECRET_KEY`: Must be provided via the `SECRET_KEY` environment variable.
    *   `PAGE_SIZE`: Uses the `DEFAULT_PAGE_SIZE` (25).
    *   **Cache:** Long-lived (600s TTL, 4096 entries).

To run in production, ensure the environment variable is set:

```bash
export SECRET_KEY="your-secure-random-string"
python run.py
```

### Testing Configuration

The `TestingConfig` class is designed for automated test suites. It sets the `TESTING` flag and uses a very small page size (5) to ensure pagination logic is triggered even with small test datasets.

*   **File:** `app/config.py`
*   **Key Settings:**
    *   `TESTING = True`
    *   `PAGE_SIZE = 5`

```python
class TestingConfig(BaseConfig):
    """Configuration for test runs."""

    TESTING: bool = True
    PAGE_SIZE: int = 5
```

### Troubleshooting: Missing Secret Key

If you attempt to initialize the application with `ProductionConfig` without setting the `SECRET_KEY` environment variable, the application will fail immediately with a `KeyError`.

**Error:**
`KeyError: 'SECRET_KEY'`

**Solution:**
Ensure the environment variable is exported before starting the server:
```bash
# Example for local production-like testing
export SECRET_KEY=$(python -c 'import os; print(os.urandom(24).hex())')
```

Note that `BaseConfig` and `DevelopmentConfig` provide a default value of `"change-me"`, so they do not require this environment variable to be set.
