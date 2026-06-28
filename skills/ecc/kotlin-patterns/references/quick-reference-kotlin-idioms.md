---
skill_id: 7de5ddac3982
usage_count: 1
last_used: 2026-06-16
---
## Quick Reference: Kotlin Idioms

| Idiom | Description |
|-------|-------------|
| `val` over `var` | Prefer immutable variables |
| `data class` | For value objects with equals/hashCode/copy |
| `sealed class/interface` | For restricted type hierarchies |
| `value class` | For type-safe wrappers with zero overhead |
| Expression `when` | Exhaustive pattern matching |
| Safe call `?.` | Null-safe member access |
| Elvis `?:` | Default value for nullables |
| `let`/`apply`/`also`/`run`/`with` | Scope functions for clean code |
| Extension functions | Add behavior without inheritance |
| `copy()` | Immutable updates on data classes |
| `require`/`check` | Precondition assertions |
| Coroutine `async`/`await` | Structured concurrent execution |
| `Flow` | Cold reactive streams |
| `sequence` | Lazy evaluation |
| Delegation `by` | Reuse implementation without inheritance |