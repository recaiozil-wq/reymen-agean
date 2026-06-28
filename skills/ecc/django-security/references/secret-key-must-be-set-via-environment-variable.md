---
skill_id: 302c64c5abca
usage_count: 1
last_used: 2026-06-16
---
# Secret key (must be set via environment variable)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY environment variable is required')