---
skill_id: b200f0642a4d
usage_count: 1
last_used: 2026-06-16
---
# Middleware
class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = (
            f"default-src {CSP_DEFAULT_SRC}; "
            f"script-src {CSP_SCRIPT_SRC}; "
            f"style-src {CSP_STYLE_SRC}; "
            f"img-src {CSP_IMG_SRC}; "
            f"connect-src {CSP_CONNECT_SRC}"
        )
        return response
```