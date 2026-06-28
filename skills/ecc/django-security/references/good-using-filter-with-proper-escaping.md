---
skill_id: f2dea0c5c786
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Using filter with proper escaping
def get_users_by_email(email):
    return User.objects.filter(email__iexact=email)  # Safe