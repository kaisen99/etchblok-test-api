---
{title: BaseConfig, description: API Reference for app.config.BaseConfig, section_id: app_config_baseconfig, section_type: class_ref}
---
# BaseConfig

Base configuration shared across all environments.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **SECRET_KEY** | `str` = change-me | Cryptographic key used for signing session cookies and protecting sensitive data, defaulting to an environment variable or a fallback string. |
| **DEBUG** | `bool` = false | Flag that enables or disables detailed error pages and development-specific features. |
| **TESTING** | `bool` = false | Flag that activates testing mode to suppress error logging and enable test-specific behavior during automated suite execution. |
| **PAGE_SIZE** | `int` = DEFAULT_PAGE_SIZE | Integer defining the number of records returned per result set, which must not exceed the system maximum page size. |

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
| `Dict[str, Any]` | A dictionary containing the environment-specific cache configuration settings used to initialize the caching backend |

---
