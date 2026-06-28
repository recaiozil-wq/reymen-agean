---
name: ecc_android-clean-architecture_references_anti-patterns-to-avoid
description: Anti-Patterns to Avoid
title: "Ecc Android Clean Architecture References Anti Patterns To Avoid"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Anti-Patterns to Avoid |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Anti-Patterns to Avoid

- Importing Android framework classes in `domain` — keep it pure Kotlin
- Exposing database entities or DTOs to the UI layer — always map to domain models
- Putting business logic in ViewModels — extract to UseCases
- Using `GlobalScope` or unstructured coroutines — use `viewModelScope` or structured concurrency
- Fat repository implementations — split into focused DataSources
- Circular module dependencies — if A depends on B, B must not depend on A
