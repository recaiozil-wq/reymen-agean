---
skill_id: 39d399023fc2
usage_count: 1
last_used: 2026-06-16
---
## File Upload Security

### File Validation

```python
import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    """Validate file extension."""
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

def validate_file_size(value):
    """Validate file size (max 5MB)."""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError('File too large. Max size is 5MB.')