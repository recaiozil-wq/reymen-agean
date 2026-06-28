---
skill_id: 16dc79ca06dc
usage_count: 1
last_used: 2026-06-16
---
## Table Definitions

### DSL Style Tables

```kotlin
// tables/UsersTable.kt
object UsersTable : UUIDTable("users") {
    val name = varchar("name", 100)
    val email = varchar("email", 255).uniqueIndex()
    val role = enumerationByName<Role>("role", 20)
    val metadata = jsonb<UserMetadata>("metadata", Json.Default).nullable()
    val createdAt = timestampWithTimeZone("created_at").defaultExpression(CurrentTimestampWithTimeZone)
    val updatedAt = timestampWithTimeZone("updated_at").defaultExpression(CurrentTimestampWithTimeZone)
}

object OrdersTable : UUIDTable("orders") {
    val userId = uuid("user_id").references(UsersTable.id)
    val status = enumerationByName<OrderStatus>("status", 20)
    val totalAmount = long("total_amount")
    val currency = varchar("currency", 3)
    val createdAt = timestampWithTimeZone("created_at").defaultExpression(CurrentTimestampWithTimeZone)
}

object OrderItemsTable : UUIDTable("order_items") {
    val orderId = uuid("order_id").references(OrdersTable.id, onDelete = ReferenceOption.CASCADE)
    val productId = uuid("product_id")
    val quantity = integer("quantity")
    val unitPrice = long("unit_price")
}
```

### Composite Tables

```kotlin
object UserRolesTable : Table("user_roles") {
    val userId = uuid("user_id").references(UsersTable.id, onDelete = ReferenceOption.CASCADE)
    val roleId = uuid("role_id").references(RolesTable.id, onDelete = ReferenceOption.CASCADE)
    override val primaryKey = PrimaryKey(userId, roleId)
}
```