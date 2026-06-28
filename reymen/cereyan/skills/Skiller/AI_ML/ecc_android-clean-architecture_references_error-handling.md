---
name: ecc_android-clean-architecture_references_error-handling
description: Error Handling
title: "Ecc Android Clean Architecture References Error Handling"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Error Handling |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
