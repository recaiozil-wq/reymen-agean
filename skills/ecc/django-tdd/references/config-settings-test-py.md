---
skill_id: 123173dac51a
usage_count: 1
last_used: 2026-06-16
---
# config/settings/test.py
from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}