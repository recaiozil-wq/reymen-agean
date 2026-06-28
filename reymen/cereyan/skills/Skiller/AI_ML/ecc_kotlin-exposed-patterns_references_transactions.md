---
name: ecc_kotlin-exposed-patterns_references_transactions
description: Transactions
title: "Ecc Kotlin Exposed Patterns References Transactions"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kotlin-exposed-patterns_references_transactions.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Transactions

### Suspend Transaction Support

```kotlin
// Good: Use newSuspendedTransaction for coroutine support
suspend fun performDatabaseOperation(): Result<User> =
    runCatching {
        newSuspendedTransaction {
            val user = UserEntity.new {
                name = "Alice"
                email = "alice@example.com"
            }
            // All operations in this block are atomic
            user.toModel()
        }
    }

// Good: Nested transactions with savepoints
suspend fun transferFunds(fromId: UUID, toId: UUID, amount: Long) {
    newSuspendedTransaction {
        val from = UserEntity.findById(fromId) ?: throw NotFoundException("User $fromId not found")
        val to = UserEntity.findById(toId) ?: throw NotFoundException("User $toId not found")

        // Debit
        from.balance -= amount
        // Credit
        to.balance += amount

        // Both succeed or both fail
    }
}
```

### Transaction Isolation

```kotlin
suspend fun readCommittedQuery(): List<User> =
    newSuspendedTransaction(transactionIsolation = Connection.TRANSACTION_READ_COMMITTED) {
        UserEntity.all().map { it.toModel() }
    }

suspend fun serializableOperation() {
    newSuspendedTransaction(transactionIsolation = Connection.TRANSACTION_SERIALIZABLE) {
        // Strictest isolation level for critical operations
    }
}
```
