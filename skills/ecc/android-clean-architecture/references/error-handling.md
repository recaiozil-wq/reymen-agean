---
skill_id: c2132cdc7ddc
usage_count: 1
last_used: 2026-06-16
---
## Error Handling

### Result/Try Pattern

Use `Result<T>` or a custom sealed type for error propagation:

```kotlin
sealed interface Try<out T> {
    data class Success<T>(val value: T) : Try<T>
    data class Failure(val error: AppError) : Try<Nothing>
}

sealed interface AppError {
    data class Network(val message: String) : AppError
    data class Database(val message: String) : AppError
    data object Unauthorized : AppError
}

// In ViewModel — map to UI state
viewModelScope.launch {
    when (val result = getItems(category)) {
        is Try.Success -> _state.update { it.copy(items = result.value, isLoading = false) }
        is Try.Failure -> _state.update { it.copy(error = result.error.toMessage(), isLoading = false) }
    }
}
```