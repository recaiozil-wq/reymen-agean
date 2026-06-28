---
name: ecc_motion-patterns_references_principles
description: Principles
title: "Ecc Motion Patterns References Principles"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_motion-patterns_references_principles.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Principles

- Every pattern imports from `motion-foundations`. No raw numbers.
- Every conditional render is wrapped in `AnimatePresence` with a `key`.
- Exit animations are always defined alongside enter animations — never as an afterthought.
- `layout` is used only for small, isolated shifts. Large subtrees get explicit transforms.
