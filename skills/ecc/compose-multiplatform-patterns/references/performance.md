---
skill_id: c05f6c233521
usage_count: 1
last_used: 2026-06-16
---
## Performance

### Stable Types for Skippable Recomposition

Mark classes as `@Stable` or `@Immutable` when all properties are stable:

```kotlin
@Immutable
data class ItemUiModel(
    val id: String,
    val title: String,
    val description: String,
    val progress: Float
)
```

### Use `key()` and Lazy Lists Correctly

```kotlin
LazyColumn {
    items(
        items = items,
        key = { it.id }  // Stable keys enable item reuse and animations
    ) { item ->
        ItemRow(item = item)
    }
}
```

### Defer Reads with `derivedStateOf`

```kotlin
val listState = rememberLazyListState()
val showScrollToTop by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 5 }
}
```

### Avoid Allocations in Recomposition

```kotlin
// BAD — new lambda and list every recomposition
items.filter { it.isActive }.forEach { ActiveItem(it, onClick = { handle(it) }) }

// GOOD — key each item so callbacks stay attached to the right row
val activeItems = remember(items) { items.filter { it.isActive } }
activeItems.forEach { item ->
    key(item.id) {
        ActiveItem(item, onClick = { handle(item) })
    }
}
```