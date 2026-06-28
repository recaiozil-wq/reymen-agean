---
skill_id: dc91d9ae4db7
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Use format_html for HTML with variables
from django.utils.html import format_html

def greet_user(username):
    return format_html('<span class="user">{}</span>', escape(username))
```

### HTTP Headers

```python