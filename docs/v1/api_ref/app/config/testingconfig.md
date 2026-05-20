---
{title: TestingConfig, description: API Reference for app.config.TestingConfig, section_id: app_config_testingconfig, section_type: class_ref}
---
# TestingConfig

Configuration for test runs.

## Attributes

| Attribute | Type | Description |
|----------|------|-------------|
| **TESTING** | `bool` = True | Flag indicating whether the application is running in a test environment, typically used to enable test-specific behavior or mock services. |
| **PAGE_SIZE** | `int` = 5 | The number of items to return per page in paginated responses during testing. |

---

## Constructor

### Signature

```python
def TestingConfig() - > null
```

---