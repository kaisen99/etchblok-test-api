---
{title: DevelopmentConfig, description: API Reference for app.config.DevelopmentConfig, section_id: app_config_developmentconfig, section_type: class_ref}
---
# DevelopmentConfig

Configuration for local development.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **DEBUG** | `bool` = True | Enables or disables debug mode to provide detailed error messages and live reloading during local development. |
| **PAGE_SIZE** | `int` = 10 | The default number of items to return per page in paginated API responses. |

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
