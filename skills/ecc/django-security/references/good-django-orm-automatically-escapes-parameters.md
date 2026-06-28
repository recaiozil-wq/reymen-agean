---
skill_id: 4c97c8081510
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Django ORM automatically escapes parameters
def get_user(username):
    return User.objects.get(username=username)  # Safe