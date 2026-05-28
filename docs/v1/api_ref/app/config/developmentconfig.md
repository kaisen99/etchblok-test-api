---
title: DevelopmentConfig
description: API Reference for app.config.DevelopmentConfig
code_symbols: [SYM#de19a9e9116dcd6a24f5962096a9ebb6f40d5857, SYM#0e49d61e810852b823b0d749c456e38617905bb6]
section_id: app_config_developmentconfig
section_type: class_ref
---
# DevelopmentConfig

Configuration for local development.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **DEBUG** | `bool` = True | Enables or disables the debug mode for the application to provide detailed error messages and live reloading during local development. |
| **PAGE_SIZE** | `int` = 10 | The default number of items to be displayed per page in paginated API responses or views. |

---



## Methods

---

#### `get_cache_config()`

```python
@classmethod
def get_cache_config() - > Dict[str, Any]
```

Generates the cache configuration settings specifically for the local development environment.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary containing the time-to-live (TTL) and maximum size constraints for the development cache. |

---
