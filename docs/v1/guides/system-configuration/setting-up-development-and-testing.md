---
title: Setting Up Development and Testing
description: How to apply specific configurations for local development and test suites, including debug modes and page sizes.
code_symbols: [SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857, SYM#2019837532635e08a2c17173935df96d18248622]
section_id: e2946b16-4dfa-4353-853e-ca9f115f7862_setting_up_development_and_testing
doc_type: how_to
section_type: guide
---
To configure the Pagemark API for different environments, you use the configuration classes defined in `app/config.py` in conjunction with the `create_app` factory function.

### Applying a Configuration

The application factory `create_app` accepts a configuration class as an argument. By default, it uses `DevelopmentConfig`.

```python
from app import create_app
from app.config import DevelopmentConfig, TestingConfig

# For local development (default)
app = create_app(DevelopmentConfig)

# For running test suites
test_app = create_app(TestingConfig)
```

### Development Configuration

The `DevelopmentConfig` class is tailored for local iteration. It enables Flask's debug mode and sets a manageable page size for manual testing.

*   **File**: `app/config.py`
*   **Debug Mode**: `DEBUG = True` (enables the interactive debugger and reloader).
*   **Pagination**: `PAGE_SIZE = 10`.
*   **Cache**: Configured with a short 30-second TTL and a maximum of 128 entries via `get_cache_config()`.

```python
@dataclass
class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG: bool = True
    PAGE_SIZE: int = 10

    def get_cache_config(self) -> Dict[str, Any]:
        return _build_cache_config(ttl=30, max_size=128)
```

### Testing Configuration

The `TestingConfig` class is designed for automated test runs. It sets the `TESTING` flag and significantly reduces the page size to make it easier to verify pagination logic with minimal test data.

*   **File**: `app/config.py`
*   **Testing Flag**: `TESTING = True`.
*   **Pagination**: `PAGE_SIZE = 5`.

```python
@dataclass
class TestingConfig(BaseConfig):
    """Configuration for test runs."""

    TESTING: bool = True
    PAGE_SIZE: int = 5
```

### Shared Defaults and Validation

Both configurations inherit from `BaseConfig`, which provides common defaults and internal validation logic.

*   **Secret Key**: Defaults to the `SECRET_KEY` environment variable or `"change-me"`.
*   **Validation**: The `_validate()` method ensures that `PAGE_SIZE` does not exceed the `MAX_PAGE_SIZE` of 100.

```python
@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "change-me"))
    DEBUG: bool = False
    TESTING: bool = False
    PAGE_SIZE: int = DEFAULT_PAGE_SIZE

    def _validate(self) -> bool:
        """Check internal invariants. Not part of the public API."""
        return bool(self.SECRET_KEY) and self.PAGE_SIZE <= MAX_PAGE_SIZE
```

### Troubleshooting

#### Page Size Limits
If you attempt to set a `PAGE_SIZE` greater than 100, the internal `_validate()` check will return `False`. While `create_app` does not currently call this validation automatically, it is used as an invariant check within the configuration layer.

#### Secret Key in Production
While `DevelopmentConfig` and `TestingConfig` provide a default `"change-me"` key, `ProductionConfig` (also in `app/config.py`) will raise a `KeyError` if the `SECRET_KEY` environment variable is not explicitly set:

```python
# From app/config.py
@dataclass
class ProductionConfig(BaseConfig):
    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
```

#### Cache Configuration Usage
Note that while `DevelopmentConfig` defines specific cache settings (TTL 30s, size 128) via `get_cache_config()`, some services like `BookmarkService` may currently use hardcoded values for their internal caches. Always verify service-level implementations if cache behavior is critical to your environment setup.
