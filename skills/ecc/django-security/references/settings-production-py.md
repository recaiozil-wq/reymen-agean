---
skill_id: e556feacab1c
usage_count: 1
last_used: 2026-06-16
---
# settings/production.py
import os

DEBUG = False  # CRITICAL: Never use True in production

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')