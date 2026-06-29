---
name: ecc_compose-multiplatform-patterns_references_anti-patterns-to-avoid
description: Anti-Patterns to Avoid
title: "Ecc Compose Multiplatform Patterns References Anti Patterns To Avoid"
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

- Using `mutableStateOf` in ViewModels when `MutableStateFlow` with `collectAsStateWithLifecycle` is safer for lifecycle
- Passing `NavController` deep into composables — pass lambda callbacks instead
- Heavy computation inside `@Composable` functions — move to ViewModel or `remember {}`
- Using `LaunchedEffect(Unit)` as a substitute for ViewModel init — it re-runs on configuration change in some setups
- Creating new object instances in composable parameters — causes unnecessary recomposition
