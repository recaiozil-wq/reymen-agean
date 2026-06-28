---
skill_id: 7a0ae359fe4c
usage_count: 1
last_used: 2026-06-16
---
## Phase 10: Documentation Review

- [ ] OpenAPI/Swagger docs up to date (`/q/swagger-ui`)
- [ ] README has setup instructions
- [ ] API changes documented
- [ ] Migration guide for breaking changes
- [ ] Configuration properties documented

Generate OpenAPI spec:
```bash
curl http://localhost:8080/q/openapi -o openapi.json
```