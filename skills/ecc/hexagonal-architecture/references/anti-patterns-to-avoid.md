---
skill_id: 949cd4a5f774
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns to Avoid

- Domain entities importing ORM models, web framework types, or SDK clients.
- Use cases reading directly from `req`, `res`, or queue metadata.
- Returning database rows directly from use cases without domain/application mapping.
- Letting adapters call each other directly instead of flowing through use-case ports.
- Spreading dependency wiring across many files with hidden global singletons.