---
name: ecc_android-clean-architecture_references_dependency-injection
description: Dependency Injection
title: "Ecc Android Clean Architecture References Dependency Injection"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Dependency Injection |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Dependency Injection

### Koin (KMP-friendly)

```kotlin
// Domain module
val domainModule = module {
    factory { GetItemsByCategoryUseCase(get()) }
    factory { ObserveUserProgressUseCase(get()) }
}

// Data module
val dataModule = module {
    single<ItemRepository> { ItemRepositoryImpl(get(), get()) }
    single { ItemLocalDataSource(get()) }
    single { ItemRemoteDataSource(get()) }
}

// Presentation module
val presentationModule = module {
    viewModelOf(::ItemListViewModel)
    viewModelOf(::DashboardViewModel)
}
```

### Hilt (Android-only)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindItemRepository(impl: ItemRepositoryImpl): ItemRepository
}

@HiltViewModel
class ItemListViewModel @Inject constructor(
    private val getItems: GetItemsByCategoryUseCase
) : ViewModel()
```
