---
name: ecc_mysql-patterns_references_output-expectations
description: Output Expectations
title: "Ecc Mysql Patterns References Output Expectations"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_mysql-patterns_references_output-expectations.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Output Expectations

When this skill is used for review, return:

1. Engine/version assumptions.
2. Highest-risk correctness, lock, security, and migration issues.
3. Exact SQL or code changes for the safe path.
4. Validation plan: `EXPLAIN`, migration dry run, lock/deadlock check, and
   rollback criteria.
5. Any MySQL/MariaDB syntax differences that affect the recommendation.
