---
skill_id: 22511c7f54a6
usage_count: 1
last_used: 2026-06-16
---
## Quick Security Checklist

| Check | Description |
|-------|-------------|
| `DEBUG = False` | Never run with DEBUG in production |
| HTTPS only | Force SSL, secure cookies |
| Strong secrets | Use environment variables for SECRET_KEY |
| Password validation | Enable all password validators |
| CSRF protection | Enabled by default, don't disable |
| XSS prevention | Django auto-escapes, don't use `&#124;safe` with user input |
| SQL injection | Use ORM, never concatenate strings in queries |
| File uploads | Validate file type and size |
| Rate limiting | Throttle API endpoints |
| Security headers | CSP, X-Frame-Options, HSTS |
| Logging | Log security events |
| Updates | Keep Django and dependencies updated |

Remember: Security is a process, not a product. Regularly review and update your security practices.