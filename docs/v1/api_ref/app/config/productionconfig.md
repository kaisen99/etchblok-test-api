---
{title: ProductionConfig, description: API Reference for app.config.ProductionConfig, section_id: app_config_productionconfig, section_type: class_ref}
---
# ProductionConfig

Configuration for production deployments.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **SECRET_KEY** | `str` = os.environ["SECRET_KEY"] | Cryptographic key used for signing session cookies and securing sensitive data, retrieved from the environment's SECRET_KEY variable. |
| **PAGE_SIZE** | `int` = DEFAULT_PAGE_SIZE | The maximum number of items to display per page in paginated API responses or views. |

---



## Methods

---

#### `get_cache_config()`

```python
@classmethod
def get_cache_config() - > Dict[str, Any]
```

Retrieves the production-specific cache configuration settings, including a 600-second TTL and a maximum size of 4096 entries.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary containing the time-to-live and capacity constraints for the application cache. |

---