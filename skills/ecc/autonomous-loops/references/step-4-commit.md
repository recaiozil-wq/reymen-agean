---
skill_id: 640e0de08086
usage_count: 1
last_used: 2026-06-16
---
# Step 4: Commit
claude -p "Create a conventional commit for all staged changes. Use 'feat: add OAuth2 login flow' as the message."
```

### Key Design Principles

1. **Each step is isolated** — A fresh context window per `claude -p` call means no context bleed between steps.
2. **Order matters** — Steps execute sequentially. Each builds on the filesystem state left by the previous.
3. **Negative instructions are dangerous** — Don't say "don't test type systems." Instead, add a separate cleanup step (see [De-Sloppify Pattern](#5-the-de-sloppify-pattern)).
4. **Exit codes propagate** — `set -e` stops the pipeline on failure.

### Variations

**With model routing:**
```bash