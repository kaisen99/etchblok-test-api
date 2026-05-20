---
{title: DevelopmentConfig, description: API Reference for app.config.DevelopmentConfig, section_id: app_config_developmentconfig, section_type: class_ref}
---
# DevelopmentConfig

Configuration for local development.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **DEBUG** | `bool` = True | Enables or disables the debug mode for the application to provide detailed error messages during local development. |
| **PAGE_SIZE** | `int` = 10 | Defines the standard number of items to be returned per page in paginated API responses or views. |

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
| `Dict[str, Any]` | A dictionary containing the Time-To-Live (TTL) and maximum size constraints for the development cache. |

---