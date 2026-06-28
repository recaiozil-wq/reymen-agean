---
name: ecc_hexagonal-architecture_references_migration-playbook
description: Migration Playbook
title: "Ecc Hexagonal Architecture References Migration Playbook"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Migration Playbook |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Migration Playbook

1. Pick one vertical slice (single endpoint/job) with frequent change pain.
2. Extract a use-case boundary with explicit input/output types.
3. Introduce outbound ports around existing infrastructure calls.
4. Move orchestration logic from controllers/services into the use case.
5. Keep old adapters, but make them delegate to the new use case.
6. Add tests around the new boundary (unit + adapter integration).
7. Repeat slice-by-slice; avoid full rewrites.

### Refactoring Existing Systems

- **Strangler approach**: keep current endpoints, route one use case at a time through new ports/adapters.
- **No big-bang rewrites**: migrate per feature slice and preserve behavior with characterization tests.
- **Facade first**: wrap legacy services behind outbound ports before replacing internals.
- **Composition freeze**: centralize wiring early so new dependencies do not leak into domain/use-case layers.
- **Slice selection rule**: prioritize high-churn, low-blast-radius flows first.
- **Rollback path**: keep a reversible toggle or route switch per migrated slice until production behavior is verified.
