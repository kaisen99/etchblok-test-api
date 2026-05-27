---
{title: TestingConfig, description: API Reference for app.config.TestingConfig, section_id: app_config_testingconfig, section_type: class_ref}
---
# TestingConfig

Configuration for test runs.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **TESTING** | `bool` = True | Flag indicating that the application is running in a test environment, typically used to enable mock behaviors or bypass security checks. |
| **PAGE_SIZE** | `int` = 5 | The number of records to return per page in paginated test results, constrained to a small fixed value for consistent test assertions. |

---

## Constructor

### Signature

```python
def TestingConfig() - > null
```

---
