---
skill_id: 9af2ad24ce31
usage_count: 1
last_used: 2026-06-16
---
# Environment variable check
python -c "from django.core.exceptions import ImproperlyConfigured; from django.conf import settings; settings.DEBUG"
```

Report:
- Vulnerable dependencies found
- Security configuration issues
- Hardcoded secrets detected
- DEBUG mode status (should be False in production)