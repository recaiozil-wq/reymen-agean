---
name: ecc_plan-orchestrate_references_available-agent-catalogue-must-pick-from-these
description: Available agent catalogue (must pick from these)
title: "Ecc Plan Orchestrate References Available Agent Catalogue Must Pick From These"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Available agent catalogue (must pick from these) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Available agent catalogue (must pick from these)

General:
- `planner` — requirement restatement, risk decomposition, step planning
- `architect` — architecture, system design, refactor proposals
- `tdd-guide` — write tests → implement → 80%+ coverage
- `code-reviewer` — generic code review
- `security-reviewer` — security audit, OWASP, secret leakage
- `refactor-cleaner` — dead code, duplicates, knip-class cleanup
- `doc-updater` — documentation, codemap, README
- `docs-lookup` — third-party library API lookups (Context7)
- `e2e-runner` — end-to-end test orchestration
- `database-reviewer` — PostgreSQL schema, migration, performance
- `harness-optimizer` — local agent harness configuration
- `loop-operator` — long-running autonomous loops
- `chief-of-staff` — multi-channel triage (rarely a fit for plan steps)

Build error resolvers:
- `build-error-resolver` (generic) / `cpp-build-resolver` / `go-build-resolver` / `java-build-resolver` / `kotlin-build-resolver` / `rust-build-resolver` / `pytorch-build-resolver`

Code reviewers:
- `python-reviewer` / `typescript-reviewer` / `go-reviewer` / `rust-reviewer` / `cpp-reviewer` / `java-reviewer` / `kotlin-reviewer` / `flutter-reviewer`

A misspelled agent name fails `/orchestrate`. Cross-check against this list before emitting.
