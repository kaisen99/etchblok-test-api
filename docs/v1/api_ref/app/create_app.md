---
title: create_app
description: API Reference for app.create_app
code_symbols: [SYM#b38e2745c556d0f02b95e096783bd0763061b004]
section_id: app_create_app
section_type: function_ref
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
| **config_class** | `Config` = DevelopmentConfig | The configuration class used to set environment-specific settings for the Flask application. |

## Returns

| Type | Description |
|------|-------------|
| `Flask` | Configured Flask application instance. |
