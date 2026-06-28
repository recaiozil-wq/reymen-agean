
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Patterns_References_Update Last Active Time |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Update last active time
            request.user.last_active = timezone.now()
            request.user.save(update_fields=['last_active'])

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging requests."""

    def process_request(self, request):
        """Log request start time."""
        request.start_time = time.time()

    def process_response(self, request, response):
        """Log request duration."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s')
        return response
```