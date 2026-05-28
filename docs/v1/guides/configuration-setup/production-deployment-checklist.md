---
title: Production Deployment Checklist
description: Essential steps for securing and optimizing your application for a production environment.
code_symbols: [SYM#d2d22b366491d800917a8a1043152349a435eed9]
section_id: 8538a0ba-fa03-4bf3-b2a3-9776f93b40a1_production_deployment_checklist
doc_type: how_to
section_type: guide
---
To prepare the application for a production environment, you must use the `ProductionConfig` class, which enforces strict security requirements and optimizes performance settings for high-traffic scenarios.

### Initialize the Application for Production

To deploy the application, create a WSGI entry point (e.g., `wsgi.py`) that passes the `ProductionConfig` class to the `create_app` factory. This overrides the default `DevelopmentConfig`.

```python
# wsgi.py
from app import create_app
from app.config import ProductionConfig

# Initialize the app with production settings
app = create_app(config_class=ProductionConfig)
```

### Configure Required Environment Variables

The `ProductionConfig` class in `app/config.py` requires the `SECRET_KEY` environment variable to be set. Unlike the base configuration, it does not provide a default value and will raise an error if it is missing.

```bash
# Set the mandatory secret key
export SECRET_KEY="your-highly-secure-random-string"

# Optional: Override default page size (defaults to 25)
export PAGE_SIZE=50
```

### Performance and Caching

When using `ProductionConfig`, the application automatically scales its internal cache to handle production loads. You can verify these settings by calling `get_cache_config()` on the configuration instance.

*   **TTL (Time to Live):** Increased to 600 seconds (10 minutes).
*   **Max Entries:** Increased to 4096 entries.
*   **Eviction Policy:** Uses Least Recently Used (LRU).

```python
from app.config import ProductionConfig

config = ProductionConfig()
cache_settings = config.get_cache_config()
# Returns: {"ttl_seconds": 600, "max_entries": 4096, "eviction": "lru"}
```

### Configure Health and Readiness Probes

The application provides internal diagnostic endpoints mounted under the `/_internal` prefix in `app/routes/_health.py`. These should be used by your load balancer or orchestrator (like Kubernetes) to monitor the service.

*   **Liveness Probe (`GET /_internal/health`):** Returns `200 OK` if the process is running.
*   **Readiness Probe (`GET /_internal/ready`):** Verifies that the `BookmarkService` is initialized and can perform database operations.

**Example Nginx/Load Balancer configuration:**
```nginx
# Restrict access to internal endpoints
location /_internal {
    allow 10.0.0.0/8; # Only allow internal network
    deny all;
    proxy_pass http://app_server;
}
```

### Troubleshooting

#### Missing SECRET_KEY
If you attempt to start the application in production without setting the `SECRET_KEY` environment variable, the application will fail to start with a `KeyError`:

```text
File "app/config.py", line 62, in ProductionConfig
    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
  File "app/config.py", line 62, in <lambda>
    SECRET_KEY: str = field(default_factory=lambda: os.environ["SECRET_KEY"])
  File ".../os.py", line 679, in __getitem__
    raise KeyError(key) from None
KeyError: 'SECRET_KEY'
```
**Solution:** Ensure `SECRET_KEY` is exported in your shell or defined in your container's environment variables.

#### Debug Mode is Enabled
If you see "Debug mode: on" in your logs, you have likely initialized the app without arguments, causing it to fall back to `DevelopmentConfig` defined in `app/__init__.py`:

```python
# INCORRECT for production
app = create_app() 

# CORRECT for production
app = create_app(config_class=ProductionConfig)
```
