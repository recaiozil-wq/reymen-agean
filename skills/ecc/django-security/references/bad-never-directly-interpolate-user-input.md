---
skill_id: e0b0d79f7230
usage_count: 1
last_used: 2026-06-16
---
# BAD: Never directly interpolate user input
def get_user_bad(username):
    return User.objects.raw(f'SELECT * FROM users WHERE username = {username}')  # VULNERABLE!