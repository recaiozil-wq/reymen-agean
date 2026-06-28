---
skill_id: bd0f6748e20b
usage_count: 1
last_used: 2026-06-16
---
# Write permissions only for owner
        return obj.author == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow admins to do anything, others read-only."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsVerifiedUser(permissions.BasePermission):
    """Allow only verified users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_verified
```

### Role-Based Access Control (RBAC)

```python