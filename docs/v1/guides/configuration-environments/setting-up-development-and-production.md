---
title: Setting Up Development and Production
description: How to configure your application for local work and live deployment using environment-specific classes.
code_symbols: [SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857, SYM#d2d22b366491d800917a8a1043152349a435eed9]
section_id: d675a553-34e3-4739-a6f7-1bcd918bcb4b_setting_up_development_and_production
doc_type: how_to
section_type: guide
---
To configure the application for different environments, you pass a configuration class from `app.config` to the application factory.

```python
from app import create_app
from app.config import ProductionConfig, DevelopmentConfig

# For local development (default)
app = create_app(DevelopmentConfig)

# For production deployment
app = create_app(ProductionConfig)
```

## Configuring for Local Development

Local development uses the `DevelopmentConfig` class, which enables debugging features and uses smaller resource limits suitable for a single developer.

By default, the entry point `run.py` initializes the application using `DevelopmentConfig`:

```python
# run.py
from app import create_app

app = create_app() # Defaults to DevelopmentConfig

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

### Development Settings
When using `DevelopmentConfig`, the following settings are applied:
- **DEBUG**: Set to `True` to enable Flask's interactive debugger.
- **PAGE_SIZE**: Reduced to `10` (from the default `25`) to make testing pagination easier with small datasets.
- **Cache**: Configured with a short TTL (30 seconds) and a small maximum size (128 entries) via `get_cache_config()`.
- **SECRET_KEY**: Defaults to `"change-me"` if the `SECRET_KEY` environment variable is not set.

## Configuring for Production

For live deployments, use the `ProductionConfig` class. This class enforces stricter security requirements and optimizes performance settings.

```python
import os
from app import create_app
from app.config import ProductionConfig

# Ensure SECRET_KEY is in the environment before starting
os.environ["SECRET_KEY"] = "your-secure-production-key"

app = create_app(ProductionConfig)
```

### Production Settings
- **SECRET_KEY**: Unlike other environments, `ProductionConfig` **requires** the `SECRET_KEY` environment variable. It does not provide a default value.
- **DEBUG**: Inherits `False` from `BaseConfig` to prevent leaking sensitive information.
- **Cache**: Optimized for high traffic with a longer TTL (600 seconds) and a larger capacity (4096 entries).
- **PAGE_SIZE**: Uses the `DEFAULT_PAGE_SIZE` of `25`.

## Troubleshooting Configuration Issues

### Missing SECRET_KEY in Production
If you attempt to initialize `ProductionConfig` without setting the `SECRET_KEY` environment variable, the application will fail immediately with a `KeyError`:

```python
# This will raise KeyError: 'SECRET_KEY'
config = ProductionConfig()
```

Always ensure your production environment (e.g., Docker, Kubernetes, or systemd) exports the `SECRET_KEY` before the application starts.

### Debug Mode in Production
The `BaseConfig` class explicitly sets `DEBUG: bool = False`. While `DevelopmentConfig` overrides this to `True`, ensure you never pass `DevelopmentConfig` to `create_app()` in a production environment, as it enables the Flask debugger which can execute arbitrary code.

### Validating Settings
The `BaseConfig` class includes a `_validate()` method that checks if the `SECRET_KEY` is present and if the `PAGE_SIZE` exceeds the `MAX_PAGE_SIZE` (100). You can use this for manual sanity checks:

```python
from app.config import DevelopmentConfig

config = DevelopmentConfig()
if not config._validate():
    raise ValueError("Invalid configuration detected")
```
