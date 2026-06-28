---
skill_id: edb61eeaf013
usage_count: 1
last_used: 2026-06-16
---
# List all extensions
mvn quarkus:list-extensions
```

### OWASP ZAP (API Security Testing)

```bash
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t http://localhost:8080/q/openapi \
  -f openapi
```

### Common Security Checks

- [ ] All secrets in environment variables (not in code)
- [ ] Input validation on all endpoints
- [ ] Authentication/authorization configured
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Passwords hashed with BCrypt
- [ ] SQL injection protection (parameterized queries)
- [ ] Rate limiting on public endpoints