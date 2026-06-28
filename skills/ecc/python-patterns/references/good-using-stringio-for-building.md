---
skill_id: fabbdcbca43a
usage_count: 1
last_used: 2026-06-16
---
# Good: Using StringIO for building
from io import StringIO

buffer = StringIO()
for item in items:
    buffer.write(str(item))
result = buffer.getvalue()
```