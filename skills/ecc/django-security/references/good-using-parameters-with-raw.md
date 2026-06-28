---
skill_id: a2e433085085
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Using parameters with raw()
def search_users(query):
    return User.objects.raw('SELECT * FROM users WHERE username = %s', [query])