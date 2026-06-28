---
skill_id: 662dc85027c7
usage_count: 1
last_used: 2026-06-16
---
## Code Smells to Avoid

- Long parameter lists → use DTO/builders
- Deep nesting → early returns
- Magic numbers → named constants
- Static mutable state → prefer dependency injection
- Silent catch blocks → log and act or rethrow
- **[QUARKUS]**: `@Singleton` where `@ApplicationScoped` is intended — breaks proxying and interception
- **[QUARKUS]**: Mixing `quarkus-resteasy-reactive` and `quarkus-resteasy` (classic) — pick one stack
- **[QUARKUS]**: Panache active-record + repository pattern in the same bounded context — pick one