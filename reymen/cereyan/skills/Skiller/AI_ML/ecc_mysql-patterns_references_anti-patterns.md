---
name: ecc_mysql-patterns_references_anti-patterns
description: Anti-Patterns
title: "Ecc Mysql Patterns References Anti Patterns"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mysql-patterns_references_anti-patterns.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

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
