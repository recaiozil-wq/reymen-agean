---
name: ecc_autonomous-loops_references_5-the-de-sloppify-pattern
description: 5.
title: "Ecc Autonomous Loops References 5 The De Sloppify Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 5.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## 5. The De-Sloppify Pattern

**An add-on pattern for any loop.** Add a dedicated cleanup/refactor step after each Implementer step.

### The Problem

When you ask an LLM to implement with TDD, it takes "write tests" too literally:
- Tests that verify TypeScript's type system works (testing `typeof x === 'string'`)
- Overly defensive runtime checks for things the type system already guarantees
- Tests for framework behavior rather than business logic
- Excessive error handling that obscures the actual code

### Why Not Negative Instructions?

Adding "don't test type systems" or "don't add unnecessary checks" to the Implementer prompt has downstream effects:
- The model becomes hesitant about ALL testing
- It skips legitimate edge case tests
- Quality degrades unpredictably

### The Solution: Separate Pass

Instead of constraining the Implementer, let it be thorough. Then add a focused cleanup agent:

```bash
