---
skill_id: a4f86f7bfc24
usage_count: 1
last_used: 2026-06-16
---
## Rules

These are non-negotiable. They apply to every component in the system.

1. **Use `motion/react` only.** Never import from `framer-motion`. Never mix the two in the same tree.
2. **`initial` must match server output.** If the server renders `opacity: 1`, the `initial` prop must also be `opacity: 1`. No exceptions.
3. **Reduced motion overrides everything.** When `useReducedMotion()` returns `true` or `prefersReduced` is `true`, all transforms are disabled. Opacity-only fades at ≤ 0.2s are the only permitted fallback.
4. **Never animate layout properties.** `width`, `height`, `top`, `left`, `margin`, `padding` are banned from `animate`. Use `transform` and `opacity` only.
5. **All token values come from `motionTokens`.** Hardcoded durations and easings in component files are forbidden.
6. **All spring configs come from the `springs` map.** Inline `stiffness`/`damping` values are forbidden.
7. **`"use client"` is required** on every file that imports from `motion/react`.
8. **Never read `window` or `navigator` at module level.** Always guard with `typeof window !== "undefined"`.