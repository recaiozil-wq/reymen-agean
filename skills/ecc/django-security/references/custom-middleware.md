---
skill_id: afb07d478d0d
usage_count: 1
last_used: 2026-06-16
---
# Custom middleware
from django.conf import settings

class SecurityHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Content-Security-Policy'] = "default-src 'self'"
        return response
```