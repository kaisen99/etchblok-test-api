---
title: Configuring for Automated Tests
description: A tutorial on preparing your application for testing using specialized configuration settings.
code_symbols: [SYM#2019837532635e08a2c17173935df96d18248622]
section_id: 23331460-92d4-4e2e-bfaf-c5a2f8a0c336_configuring_for_automated_tests
doc_type: tutorial
section_type: guide
---
In this tutorial, you will learn how to prepare the application for automated testing by utilizing the specialized `TestingConfig` class. By the end of this guide, you will be able to initialize a Flask application instance specifically configured for a test environment, featuring reduced pagination limits and enabled testing flags.

### Prerequisites

To follow this tutorial, you need the application environment set up with Flask and the project's internal modules accessible. Ensure you are familiar with the application factory pattern used in `app/__init__.py`.

### Step 1: Inspect the Testing Configuration

The application uses a hierarchy of configuration classes defined in `app/config.py`. The `TestingConfig` class is specifically designed to override default settings for test runs.

```python
from dataclasses import dataclass
from app.config import BaseConfig

@dataclass
class TestingConfig(BaseConfig):
    """Configuration for test runs."""

    TESTING: bool = True
    PAGE_SIZE: int = 5
```

By using `TestingConfig`, you achieve two critical changes:
1.  **`TESTING = True`**: This enables Flask's testing mode, which allows for better error reporting and behavior during test execution.
2.  **`PAGE_SIZE = 5`**: The default `PAGE_SIZE` in `BaseConfig` is 25. Reducing this to 5 in the test environment allows you to test pagination logic (like "next page" links) using much smaller datasets.

### Step 2: Initialize the App with the Testing Configuration

The application provides a factory function, `create_app`, in `app/__init__.py`. This function accepts a `config_class` argument, which it uses to populate the Flask app's configuration.

To create a test instance of the app, pass `TestingConfig` to this factory:

```python
from app import create_app
from app.config import TestingConfig

# Create the app instance using the testing configuration
app = create_app(config_class=TestingConfig)
```

The `create_app` function applies the configuration using `app.config.from_object(config_class)`, as seen in the implementation:

```python
def create_app(config_class=DevelopmentConfig) -> Flask:
    """Application factory.
    ...
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # ... blueprint registration ...
    
    return app
```

### Step 3: Verify the Test Environment

Once the app is initialized, you can verify that the settings from `TestingConfig` have been correctly applied. This is useful for ensuring your test suite is running against the expected environment.

```python
app = create_app(config_class=TestingConfig)

# Verify the configuration values
assert app.config['TESTING'] is True
assert app.config['PAGE_SIZE'] == 5
assert app.config['SECRET_KEY'] == "change-me"  # Inherited from BaseConfig
```

Note that `TestingConfig` inherits from `BaseConfig`, which provides a default `SECRET_KEY` of `"change-me"` via `os.environ.get`. This ensures that tests can run without requiring a real secret key to be set in the environment, unlike `ProductionConfig` which requires one.

### Step 4: Use the App in a Test Context

With the configured `app` instance, you can now use Flask's test client to perform requests against your API. This is the standard way to verify your routes and logic.

```python
with app.test_client() as client:
    # Example: Testing the health check endpoint
    response = client.get('/_internal/health')
    assert response.status_code == 200
```

### Summary and Next Steps

You have successfully configured the application for testing by:
1.  Identifying the `TestingConfig` class and its specific overrides.
2.  Using the `create_app` factory to inject the test configuration.
3.  Verifying that the environment-specific settings (like reduced `PAGE_SIZE`) are active.

Next, you can explore the `app.routes` blueprints to see which endpoints you can test using this setup, or examine `app.db.repository` to understand how the in-memory database is initialized during the `create_app` process.
