---
{title: ProductionConfig, description: API Reference for app.config.ProductionConfig, section_id: app_config_productionconfig, section_type: class_ref}
---
# ProductionConfig

Configuration for production deployments.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **SECRET_KEY** | `str` = os.environ["SECRET_KEY"] | Cryptographic key used for signing session cookies and securing sensitive data, sourced from the environment's SECRET_KEY variable. |
| **PAGE_SIZE** | `int` = DEFAULT_PAGE_SIZE | The maximum number of records to return in a single paginated API response, initialized to the system default. |

---



## Methods

---

#### `get_cache_config()`

```python
@classmethod
def get_cache_config() - > Dict[str, Any]
```

Generates the production-specific cache configuration settings.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary containing the TTL (Time To Live) and maximum size constraints for the production cache layer. |

---
