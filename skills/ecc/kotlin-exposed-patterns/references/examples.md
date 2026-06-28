---
skill_id: bfebe34154a0
usage_count: 1
last_used: 2026-06-16
---
## Examples

### DSL Query

```kotlin
suspend fun findUserById(id: UUID): UserRow? =
    newSuspendedTransaction {
        UsersTable.selectAll()
            .where { UsersTable.id eq id }
            .map { it.toUser() }
            .singleOrNull()
    }
```

### DAO Entity Usage

```kotlin
suspend fun createUser(request: CreateUserRequest): User =
    newSuspendedTransaction {
        UserEntity.new {
            name = request.name
            email = request.email
            role = request.role
        }.toModel()
    }
```

### HikariCP Configuration

```kotlin
val hikariConfig = HikariConfig().apply {
    driverClassName = config.driver
    jdbcUrl = config.url
    username = config.username
    password = config.password
    maximumPoolSize = config.maxPoolSize
    isAutoCommit = false
    transactionIsolation = "TRANSACTION_READ_COMMITTED"
    validate()
}
```