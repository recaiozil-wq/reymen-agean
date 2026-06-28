---
skill_id: f29fabe637a4
usage_count: 1
last_used: 2026-06-16
---
## Replication

Read replicas can lag. Do not route read-your-own-write paths, checkout flows,
permission checks, or idempotency-key reads to a replica immediately after a
write.

```sql
-- MySQL legacy terminology, still common in existing fleets
SHOW SLAVE STATUS\G;

-- Newer terminology where supported
SHOW REPLICA STATUS\G;
```

Check the engine/version before standardizing on one command. Monitor replica
SQL thread health, IO thread health, and lag, not just whether the TCP
connection is alive.