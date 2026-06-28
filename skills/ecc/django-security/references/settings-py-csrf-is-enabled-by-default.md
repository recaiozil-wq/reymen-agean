---
skill_id: a104af143d4f
usage_count: 1
last_used: 2026-06-16
---
# settings.py - CSRF is enabled by default
CSRF_COOKIE_SECURE = True  # Only send over HTTPS
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access
CSRF_COOKIE_SAMESITE = 'Lax'  # Prevent CSRF in some cases
CSRF_TRUSTED_ORIGINS = ['https://example.com']  # Trusted domains