---
{title: BaseConfig, description: API Reference for app.config.BaseConfig, section_id: app_config_baseconfig, section_type: class_ref}
---
# BaseConfig

Base configuration shared across all environments.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **SECRET_KEY** | `str` = change-me | Cryptographic key used for signing session cookies and securing sensitive data, defaulting to the 'SECRET_KEY' environment variable or 'change-me'. |
| **DEBUG** | `bool` = false | Boolean flag that enables or disables debug mode to provide detailed error messages and live reloading during development. |
| **TESTING** | `bool` = false | Boolean flag that enables testing mode to suppress error mailing and allow for isolated unit testing environments. |
| **PAGE_SIZE** | `int` = DEFAULT_PAGE_SIZE | The number of records to return per page in paginated API responses or list views. |

---



## Methods

---

#### `get_cache_config()`

```python
@classmethod
def get_cache_config() - > Dict[str, Any]
```

Return cache settings for this environment.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary containing the specific cache configuration parameters for the current environment |

---
