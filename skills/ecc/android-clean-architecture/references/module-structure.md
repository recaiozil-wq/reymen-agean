---
skill_id: 262ea19c412c
usage_count: 1
last_used: 2026-06-16
---
## Module Structure

### Recommended Layout

```
project/
├── app/                  # Android entry point, DI wiring, Application class
├── core/                 # Shared utilities, base classes, error types
├── domain/               # UseCases, domain models, repository interfaces (pure Kotlin)
├── data/                 # Repository implementations, DataSources, DB, network
├── presentation/         # Screens, ViewModels, UI models, navigation
├── design-system/        # Reusable Compose components, theme, typography
└── feature/              # Feature modules (optional, for larger projects)
    ├── auth/
    ├── settings/
    └── profile/
```

### Dependency Rules

```
app → presentation, domain, data, core
presentation → domain, design-system, core
data → domain, core
domain → core (or no dependencies)
core → (nothing)
```

**Critical**: `domain` must NEVER depend on `data`, `presentation`, or any framework. It contains pure Kotlin only.