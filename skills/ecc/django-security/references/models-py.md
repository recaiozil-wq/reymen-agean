---
skill_id: 9791ade99736
usage_count: 1
last_used: 2026-06-16
---
# models.py
class Document(models.Model):
    file = models.FileField(
        upload_to='documents/',
        validators=[validate_file_extension, validate_file_size]
    )
```

### Secure File Storage

```python