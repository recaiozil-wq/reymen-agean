---
skill_id: e2d2fc80ce4f
usage_count: 1
last_used: 2026-06-16
---
# Good: Clear and readable
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]