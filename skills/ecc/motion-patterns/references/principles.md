---
skill_id: 0fc6de89aa1f
usage_count: 1
last_used: 2026-06-16
---
## Principles

- Every pattern imports from `motion-foundations`. No raw numbers.
- Every conditional render is wrapped in `AnimatePresence` with a `key`.
- Exit animations are always defined alongside enter animations — never as an afterthought.
- `layout` is used only for small, isolated shifts. Large subtrees get explicit transforms.