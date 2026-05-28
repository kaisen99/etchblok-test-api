---
title: ProductionConfig
description: API Reference for app.config.ProductionConfig
code_symbols: [SYM#d2d22b366491d800917a8a1043152349a435eed9, SYM#0e49d61e810852b823b0d749c456e38617905bb6]
section_id: app_config_productionconfig
section_type: class_ref
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

Retrieves the production-specific cache configuration settings.

#### Returns

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | A dictionary containing the time-to-live (TTL) and maximum size constraints for the cache layer. |

---
