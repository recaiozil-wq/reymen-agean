---
skill_id: 62e2721669c2
usage_count: 1
last_used: 2026-06-16
---
## Model Policies
- Default model: use the repository or harness default.
- @dev tasks: prefer a higher-reasoning model for complex architecture.
- @researcher tasks: use the configured research-capable model and approved search tools.
- Cost ceiling: warn before exceeding the project's configured spend threshold.
```

### Key Principle

The kernel should be **small and declarative**. Routing logic lives in plain markdown tables, not code. This makes the system inspectable and editable without debugging.