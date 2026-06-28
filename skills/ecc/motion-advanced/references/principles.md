---
skill_id: 0fc6de89aa1f
usage_count: 1
last_used: 2026-06-16
---
## Principles

- Physics-based motion (`useSpring`, `springs.*`) always feels more natural than duration-based for direct manipulation.
- `useMotionValue` + `useTransform` computes derived values without triggering re-renders.
- `useAnimate` sequences are imperative and interrupt-safe — calling `animate()` mid-flight cancels the previous animation automatically.
- Motion values (`useMotionValue`, `useSpring`) are SSR-safe and do not cause hydration errors.