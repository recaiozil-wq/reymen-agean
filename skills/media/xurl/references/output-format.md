---
skill_id: 1e086202b692
usage_count: 1
last_used: 2026-06-16
---
## Output Format

All commands return JSON to stdout. Structure mirrors X API v2:

```json
{ "data": { "id": "1234567890", "text": "Hello world!" } }
```

Errors are also JSON:

```json
{ "errors": [ { "message": "Not authorized", "code": 403 } ] }
```

---