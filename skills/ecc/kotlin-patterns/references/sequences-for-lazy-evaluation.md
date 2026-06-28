---
skill_id: 54c8de68b2a6
usage_count: 1
last_used: 2026-06-16
---
## Sequences for Lazy Evaluation

```kotlin
// Good: Use sequences for large collections with multiple operations
val result = users.asSequence()
    .filter { it.isActive }
    .map { it.email }
    .filter { it.endsWith("@company.com") }
    .take(10)
    .toList()

// Good: Generate infinite sequences
val fibonacci: Sequence<Long> = sequence {
    var a = 0L
    var b = 1L
    while (true) {
        yield(a)
        val next = a + b
        a = b
        b = next
    }
}

val first20 = fibonacci.take(20).toList()
```