---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

| Rule | Reason |
|---|---|
| `migrate deploy` in CI/CD, `migrate dev` only locally | `migrate dev` can reset the DB on drift |
| Map entities to response DTOs | Prevents leaking internal fields |
| Catch `PrismaClientKnownRequestError` at service boundary | Translate to domain errors |
| Prefer `*OrThrow` methods over manual null checks | Throws P2025 automatically; use `findFirstOrThrow` when filtering non-unique fields |
| `connection_limit=1` + external pooler in serverless | Prevents connection exhaustion |
| Always provide `where` on `deleteMany` | Prevents accidental table wipe |
| Set `updatedAt: new Date()` manually in `updateMany` | `@updatedAt` skips bulk writes |