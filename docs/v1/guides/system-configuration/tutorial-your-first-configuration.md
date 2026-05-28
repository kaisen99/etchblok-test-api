---
title: 'Tutorial: Your First Configuration'
description: A beginner-friendly guide to creating and activating a new configuration profile for a custom environment.
code_symbols: [SYM#2a6650db2a04b7eb03cfe02be64ee94b0e0e0e18, SYM#7dcc662114beb69932d02b031db76440ec4fc17c, SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857]
section_id: 1390108e-86af-4934-9eb5-ed8905856e7c_tutorial-_your_first_configuration
doc_type: tutorial
section_type: guide
---
In this tutorial, you will create a custom configuration profile for a staging environment. You will learn how to inherit from the base configuration, override default settings like page sizes and cache behavior, and activate your new profile in the application factory.

### Prerequisites

Before starting, ensure you have the project set up and are familiar with the following files:
- `app/config.py`: Where configuration classes are defined.
- `app/__init__.py`: Where the `create_app` factory resides.
- `run.py`: The entry point for the application.

### Step 1: Define the Staging Configuration

Open `app/config.py`. You will see existing classes like `BaseConfig` and `DevelopmentConfig`. To create a staging environment, you should inherit from `BaseConfig` to ensure you have all the required default settings.

Add the following code to `app/config.py`:

```python
from dataclasses import dataclass
from app.config import BaseConfig, _build_cache_config

@dataclass
class StagingConfig(BaseConfig):
    """Configuration for the staging environment."""
    DEBUG: bool = False
    PAGE_SIZE: int = 50
```

By inheriting from `BaseConfig`, your `StagingConfig` automatically receives the default `SECRET_KEY` logic and `TESTING` status. Here, we've explicitly disabled `DEBUG` mode and increased the `PAGE_SIZE` to 50.

### Step 2: Customize Cache Settings

The application uses a `get_cache_config()` method to determine cache behavior. In staging, you might want a longer Time-To-Live (TTL) than development but a smaller cache than production.

Update your `StagingConfig` in `app/config.py` to override this method:

```python
@dataclass
class StagingConfig(BaseConfig):
    """Configuration for the staging environment."""
    DEBUG: bool = False
    PAGE_SIZE: int = 50

    def get_cache_config(self) -> Dict[str, Any]:
        # Set TTL to 120 seconds and max size to 512 entries
        return _build_cache_config(ttl=120, max_size=512)
```

This uses the internal `_build_cache_config` helper to generate a standardized configuration dictionary that the rest of the application expects.

### Step 3: Activate the Configuration

To use your new configuration, you need to pass it to the `create_app` factory. The factory in `app/__init__.py` is designed to accept a configuration class.

Modify your `run.py` (or create a new `run_staging.py`) to import and use `StagingConfig`:

```python
from app import create_app
from app.config import StagingConfig

# Initialize the app with the custom StagingConfig
app = create_app(config_class=StagingConfig)

if __name__ == "__main__":
    # Note: We manually set debug=False to match our config
    app.run(debug=app.config["DEBUG"], port=5000)
```

The `create_app` function uses `app.config.from_object(config_class)` to load these settings into Flask's internal configuration object.

### Step 4: Verify the Configuration

You can verify that your configuration is active by checking the Flask app's config values. You can add a temporary print statement in `run.py` or use a shell:

```python
from app import create_app
from app.config import StagingConfig

app = create_app(config_class=StagingConfig)
print(f"Active Page Size: {app.config['PAGE_SIZE']}")
# Output: Active Page Size: 50
```

### Important Considerations

*   **Validation**: `BaseConfig` includes a `_validate()` method. If you set `PAGE_SIZE` higher than `MAX_PAGE_SIZE` (100), this internal check will fail.
*   **Secret Keys**: While `BaseConfig` provides a default "change-me" key, you should set the `SECRET_KEY` environment variable in staging. If you were to inherit from `ProductionConfig` instead, the application would raise a `KeyError` if the environment variable is missing.
*   **Default Factory**: The `create_app` function in `app/__init__.py` defaults to `DevelopmentConfig` if no argument is provided. Always ensure you explicitly pass your custom class when running in non-development environments.

### Next Steps

Now that you have a custom configuration, you can explore adding environment-specific blueprints or middleware in `app/__init__.py` by checking the values within `app.config`.
