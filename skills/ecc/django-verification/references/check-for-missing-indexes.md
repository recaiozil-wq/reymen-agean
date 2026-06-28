---
skill_id: a85710cd99c2
usage_count: 1
last_used: 2026-06-16
---
# Check for missing indexes
python manage.py shell << EOF
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT table_name, index_name FROM information_schema.statistics WHERE table_schema = 'public'")
    print(cursor.fetchall())
EOF
```

Report:
- Number of queries per page (should be < 50 for typical pages)
- Missing database indexes
- Duplicate queries detected