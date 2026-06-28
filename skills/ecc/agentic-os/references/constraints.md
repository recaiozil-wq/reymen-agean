---
skill_id: d178923285d6
usage_count: 1
last_used: 2026-06-16
---
## Constraints
- Always write tests for new features
- Never commit directly to `main`; use feature branches
- Prefer editing existing files over creating new ones
- Keep functions under 50 lines when possible
```

### Multi-Agent Collaboration Pattern

When a task spans multiple agents, the kernel runs them sequentially or in parallel:

```
User: "Build a landing page and write the launch blog post"

Kernel routing:
1. @dev - "Build a landing page with [requirements]"
2. @writer - "Write a launch blog post for [product] using the landing page copy"
3. Kernel synthesizes both outputs into a unified response
```

For parallel execution, use Claude Code's background task capability or shell scripts that invoke Claude Code with specific agent contexts.