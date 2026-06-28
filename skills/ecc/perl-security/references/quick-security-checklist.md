---
skill_id: 22511c7f54a6
usage_count: 1
last_used: 2026-06-16
---
## Quick Security Checklist

| Check | What to Verify |
|---|---|
| Taint mode | `-T` flag on CGI/web scripts |
| Input validation | Allowlist patterns, length limits |
| File operations | Three-arg open, path traversal checks |
| Process execution | List-form system, no shell interpolation |
| SQL queries | DBI placeholders, never interpolate |
| HTML output | `encode_entities()`, template auto-escape |
| CSRF tokens | Generated, verified on state-changing requests |
| Session config | Secure, HttpOnly, SameSite cookies |
| HTTP headers | CSP, X-Frame-Options, HSTS |
| Dependencies | Pinned versions, audited modules |
| Regex safety | No nested quantifiers, anchored patterns |
| Error messages | No stack traces or paths leaked to users |