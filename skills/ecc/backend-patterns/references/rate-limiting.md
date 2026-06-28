---
skill_id: b1e47b6225c7
usage_count: 1
last_used: 2026-06-16
---
## Rate Limiting

Rate limiting must use a shared store such as Redis, a gateway, or the
platform's native limiter. Do not use per-process in-memory counters for
production APIs: they reset on deploy, split across replicas, and fail open in
serverless or multi-instance environments.

Keep the backend layer responsible for choosing the integration point and error
shape; use `api-design` for the HTTP contract and `security-review` for abuse
case review.