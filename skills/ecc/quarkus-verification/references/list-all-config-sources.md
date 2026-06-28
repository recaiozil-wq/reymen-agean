---
skill_id: e0b6b630a7e9
usage_count: 1
last_used: 2026-06-16
---
# List all config sources
curl http://localhost:8080/q/dev/io.quarkus.quarkus-vertx-http/config
```

### Environment-Specific Checks

- [ ] Database URLs configured per environment
- [ ] Secrets externalized (Vault, env vars)
- [ ] Logging levels appropriate
- [ ] CORS origins set correctly
- [ ] Rate limiting configured
- [ ] Monitoring/tracing enabled