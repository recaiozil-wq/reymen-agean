---
skill_id: 416760f24f57
usage_count: 1
last_used: 2026-06-16
---
# Check for migration conflicts
python manage.py makemigrations --merge  # Only if conflicts exist
```

Report:
- Number of pending migrations
- Any migration conflicts
- Model changes without migrations