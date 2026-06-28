---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

| Anti-Pattern | Risk | Better Pattern |
| --- | --- | --- |
| `SELECT *` in hot paths | Over-fetching and brittle clients | Select explicit columns |
| Deep `OFFSET` pagination | Linear scans and slow pages | Keyset pagination |
| No index on foreign-key joins | Slow joins and lock-heavy deletes | Index FK columns intentionally |
| Long transactions | Lock waits and large undo history | Commit small units of work |
| Direct DML against `mysql.user` | Grant-table corruption risk | Use `CREATE USER`, `ALTER USER`, `DROP USER` |
| Application user with admin grants | High blast radius | Least-privilege runtime user |
| Pool recycle above `wait_timeout` | Stale pooled connections | Recycle below timeout and pre-ping |
| Replica reads after writes | Stale user-facing state | Pin read-after-write flows to primary |