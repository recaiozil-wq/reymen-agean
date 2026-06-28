---
skill_id: 47fd2401eb93
usage_count: 1
last_used: 2026-06-16
---
## Flaky Tests Guardrails

- Never use `sleep` for synchronization; use condition variables or latches.
- Make temp directories unique per test and always clean them.
- Avoid real time, network, or filesystem dependencies in unit tests.
- Use deterministic seeds for randomized inputs.