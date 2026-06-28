---
skill_id: a51c9e4ed60f
usage_count: 1
last_used: 2026-06-16
---
# middleware/active_user_middleware.py
import time
from django.utils.deprecation import MiddlewareMixin

class ActiveUserMiddleware(MiddlewareMixin):
    """Middleware to track active users."""

    def process_request(self, request):
        """Process incoming request."""
        if request.user.is_authenticated: