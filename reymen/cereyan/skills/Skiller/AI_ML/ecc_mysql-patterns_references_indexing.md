---
name: ecc_mysql-patterns_references_indexing
description: Indexing
title: "Ecc Mysql Patterns References Indexing"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mysql-patterns_references_indexing.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Indexing

Composite index order usually follows equality predicates first, then range or
sort columns:

```sql
CREATE INDEX idx_orders_account_status_created
    ON orders (account_id, status, created_at);

SELECT id, total
FROM orders
WHERE account_id = ?
  AND status = 'pending'
  AND created_at >= ?
ORDER BY created_at DESC
LIMIT 50;
```

Use `EXPLAIN` before adding or changing an index:

```sql
EXPLAIN
SELECT id, total
FROM orders
WHERE account_id = 123 AND status = 'pending'
ORDER BY created_at DESC
LIMIT 50;
```

Signals to investigate:

| Field | Risk Signal |
| --- | --- |
| `type` | `ALL` on a large table |
| `key` | `NULL` when a selective predicate exists |
| `rows` | Very high row estimate for an interactive path |
| `Extra` | `Using temporary`, `Using filesort`, or broad `Using where` |

Avoid adding indexes blindly. Each index increases write cost, migration time,
backup size, and buffer-pool pressure.
