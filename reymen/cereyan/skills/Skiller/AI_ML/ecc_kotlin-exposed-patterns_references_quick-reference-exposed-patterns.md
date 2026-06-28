---
name: ecc_kotlin-exposed-patterns_references_quick-reference-exposed-patterns
description: "Quick Reference: Exposed Patterns"
title: "Ecc Kotlin Exposed Patterns References Quick Reference Exposed Patterns"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kotlin-exposed-patterns_references_quick-reference-exposed-patterns.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Quick Reference: Exposed Patterns

| Pattern | Description |
|---------|-------------|
| `object Table : UUIDTable("name")` | Define table with UUID primary key |
| `newSuspendedTransaction { }` | Coroutine-safe transaction block |
| `Table.selectAll().where { }` | Query with conditions |
| `Table.insertAndGetId { }` | Insert and return generated ID |
| `Table.update({ condition }) { }` | Update matching rows |
| `Table.deleteWhere { }` | Delete matching rows |
| `Table.batchInsert(items) { }` | Efficient bulk insert |
| `innerJoin` / `leftJoin` | Join tables |
| `orderBy` / `limit` / `offset` | Sort and paginate |
| `count()` / `sum()` / `avg()` | Aggregation functions |

**Remember**: Use the DSL style for simple queries and the DAO style when you need entity lifecycle management. Always use `newSuspendedTransaction` for coroutine support, and wrap database operations behind a repository interface for testability.
