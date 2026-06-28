---
skill_id: 8350f46b741e
usage_count: 1
last_used: 2026-06-16
---
# reading .env file
environ.Env.read_env()

SECRET_KEY = env('DJANGO_SECRET_KEY')
DATABASE_URL = env('DATABASE_URL')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')