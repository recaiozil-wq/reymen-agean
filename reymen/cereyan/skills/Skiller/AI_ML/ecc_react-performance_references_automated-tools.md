---
name: ecc_react-performance_references_automated-tools
description: Automated Tools
title: "Ecc React Performance References Automated Tools"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Automated Tools |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Automated Tools

Many of these rules are now automated:

- **Next.js 13.5+ Optimize Package Imports** — barrel import optimization
- **React Compiler** (RFC, in canary) — auto-memoization
- **Turbopack** — faster builds, better tree-shaking
- **Bundle Analyzer** (`@next/bundle-analyzer`) — visualize first-load JS

When the project ships React Compiler, demote `rerender-*` manual memoization rules to "review-only" — the compiler handles them. Manual `useMemo`/`useCallback` becomes unnecessary noise.
