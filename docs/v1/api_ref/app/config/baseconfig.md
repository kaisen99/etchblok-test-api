---
title: BaseConfig
description: API Reference for app.config.BaseConfig
code_symbols: [SYM#7dcc662114beb69932d02b031db76440ec4fc17c, SYM#0e49d61e810852b823b0d749c456e38617905bb6, SYM#af12fc21dfc802b33c302dbac85300dea45d5c2c]
section_id: app_config_baseconfig
section_type: class_ref
---
# BaseConfig

Base configuration shared across all environments.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **SECRET_KEY** | `str` = change-me | Cryptographic key used for signing session cookies and protecting sensitive data, defaulting to an environment variable or a fallback string. |
| **DEBUG** | `bool` = false | Flag that enables or disables detailed error pages and development-specific features. |
| **TESTING** | `bool` = false | Boolean toggle that activates testing mode to suppress email sending and enable test-specific error reporting. |
| **PAGE_SIZE** | `int` = DEFAULT_PAGE_SIZE | Integer defining the number of records returned per request in paginated responses, constrained by a system-wide maximum. |

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
| `Dict[str, Any]` | A dictionary containing the environment-specific cache configuration settings |

---
