---
name: ecc_kotlin-exposed-patterns_references_how-it-works
description: How It Works
title: "Ecc Kotlin Exposed Patterns References How It Works"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kotlin-exposed-patterns_references_how-it-works.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## How It Works

Exposed provides two query styles: DSL for direct SQL-like expressions and DAO for entity lifecycle management. HikariCP manages a pool of reusable database connections configured via `HikariConfig`. Flyway runs versioned SQL migration scripts at startup to keep the schema in sync. All database operations run inside `newSuspendedTransaction` blocks for coroutine safety and atomicity. The repository pattern wraps Exposed queries behind an interface so business logic stays decoupled from the data layer and tests can use an in-memory H2 database.
