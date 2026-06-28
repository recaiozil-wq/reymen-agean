---
skill_id: f090a1b014e1
usage_count: 1
last_used: 2026-06-16
---
# Verify environment variables
python -c "import os; import environ; print('DJANGO_SECRET_KEY set' if os.environ.get('DJANGO_SECRET_KEY') else 'MISSING: DJANGO_SECRET_KEY')"
```

If environment is misconfigured, stop and fix.