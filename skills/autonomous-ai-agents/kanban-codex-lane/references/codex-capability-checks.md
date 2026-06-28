---
skill_id: 372ef5437aa3
usage_count: 1
last_used: 2026-06-16
---
## Codex Capability Checks

Run these before spawning Codex. Missing Codex is a normal reason to skip the lane, not a task blocker if ReYMeN can do the task directly.

```bash
command -v codex
codex --version
codex features list | grep -i goals || true
```

If `/goal` support is required, enable or launch with the feature flag only after checking availability:

```bash
codex features enable goals || true
codex --enable goals --version
```

Authentication can be via `OPENAI_API_KEY` or the Codex CLI OAuth state (often `~/.codex/auth.json`). Do not print token files. A missing `OPENAI_API_KEY` is not proof that auth is unavailable.