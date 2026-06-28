---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

- Structure the app around clear boundaries (controllers -> services/actions -> models).
- Use explicit bindings and scoped bindings to keep routing predictable; still enforce authorization for access control.
- Favor typed models, casts, and scopes to keep domain logic consistent.
- Keep IO-heavy work in queues and cache expensive reads.
- Centralize config in `config/*` and keep environments explicit.