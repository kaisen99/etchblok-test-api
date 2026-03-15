---
{title: BaseConfig, description: API Reference for app.config.BaseConfig, section_id: app_config_baseconfig, section_type: class_ref}
---
# BaseConfig
Base configuration shared across all environments. Cause this is test checkin!
## Attributes
| Attribute | Type | Description |
| --- | --- | --- |
| **SECRET_KEY** | `str` = change-me | Cryptographic key used for signing session cookies and securing sensitive data, defaulting to an environment variable or a fallback string. |
| **DEBUG** | `bool` = false | Flag that enables or disables the application's debug mode for enhanced error reporting and development tools. |
| **TESTING** | `bool` = false | Boolean toggle that activates the testing mode to modify behavior for automated test suites. |
| **PAGE_SIZE** | `int` = DEFAULT_PAGE_SIZE | The number of records to return per page in paginated responses, constrained by the system's maximum page size. |
---
## Constructor
### Signature
```python
def BaseConfig() - > null
```
---
## Methods
---
#### `get_cache_config()`
```python
@classmethod
def get_cache_config() - > Dict[string, Any]
```
Return cache settings for this environment.
#### Returns
| Type | Description |
| --- | --- |
| `Dict[string, Any]` | A dictionary containing the cache configuration settings specific to the current environment. |
---