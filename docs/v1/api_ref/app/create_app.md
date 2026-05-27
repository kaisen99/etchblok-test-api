---
{title: create_app, description: API Reference for app.create_app, section_id: app_create_app, section_type: function_ref}
---
# create_app

Application factory.

Creates and configures the Flask application, registers blueprints,
and initialises the in-memory database.

```python
def create_app(
    config_class: Config = DevelopmentConfig
) - > Flask
```

Application factory. Creates and configures the Flask application, registers blueprints, and initialises the in-memory database.

## Parameters

| Name | Type | Description |
|------|------|-------------|
| **config_class** | `Config` = DevelopmentConfig | Configuration class to use for setting application-wide settings and environment variables. |

## Returns

| Type | Description |
|------|-------------|
| `Flask` | Configured Flask application instance. |
