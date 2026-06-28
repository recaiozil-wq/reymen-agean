---
skill_id: b04a2630fbf5
usage_count: 1
last_used: 2026-06-16
---
## Core Principles

1. **Fail fast and loudly** — surface errors at the boundary where they occur; don't bury them
2. **Typed errors over string messages** — errors are first-class values with structure
3. **User messages ≠ developer messages** — show friendly text to users, log full context server-side
4. **Never swallow errors silently** — every `catch` block must either handle, re-throw, or log
5. **Errors are part of your API contract** — document every error code a client may receive