---
skill_id: 4819c0bd1d1a
usage_count: 1
last_used: 2026-06-16
---
# permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow only owners to edit objects."""

    def has_object_permission(self, request, view, obj):