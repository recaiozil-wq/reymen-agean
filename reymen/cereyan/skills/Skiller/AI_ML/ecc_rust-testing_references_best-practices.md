---
name: ecc_rust-testing_references_best-practices
description: Best Practices
title: "Ecc Rust Testing References Best Practices"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Best Practices |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Best Practices

**DO:**
- Write tests FIRST (TDD)
- Use `#[cfg(test)]` modules for unit tests
- Test behavior, not implementation
- Use descriptive test names that explain the scenario
- Prefer `assert_eq!` over `assert!` for better error messages
- Use `?` in tests that return `Result` for cleaner error output
- Keep tests independent — no shared mutable state

**DON'T:**
- Use `#[should_panic]` when you can test `Result::is_err()` instead
- Mock everything — prefer integration tests when feasible
- Ignore flaky tests — fix or quarantine them
- Use `sleep()` in tests — use channels, barriers, or `tokio::time::pause()`
- Skip error path testing
