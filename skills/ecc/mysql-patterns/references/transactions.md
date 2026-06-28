---
skill_id: c15b977dd993
usage_count: 1
last_used: 2026-06-16
---
## Transactions

Keep transactions short and lock rows in a consistent order:

```sql
START TRANSACTION;

SELECT id, balance
FROM accounts
WHERE id IN (?, ?)
ORDER BY id
FOR UPDATE;

UPDATE accounts SET balance = balance - ? WHERE id = ?;
UPDATE accounts SET balance = balance + ? WHERE id = ?;

COMMIT;
```

Deadlock and lock-wait checklist:

- Lock rows in a deterministic order across code paths.
- Do external API calls before opening the transaction, not inside it.
- Add indexes for predicates used in `UPDATE`, `DELETE`, and locking reads.
- On deadlock, roll back and retry the whole transaction with a bounded retry
  budget.
- Capture `SHOW ENGINE INNODB STATUS\G` soon after a deadlock; it is overwritten
  by later events.

Queue-style worker claim:

```sql
START TRANSACTION;

SELECT id
FROM jobs
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;

UPDATE jobs
SET status = 'processing', started_at = CURRENT_TIMESTAMP
WHERE id = ?;

COMMIT;
```

Use `SKIP LOCKED` only for queue-like workloads where skipping a locked row is
acceptable. It is not a replacement for normal transactional consistency.