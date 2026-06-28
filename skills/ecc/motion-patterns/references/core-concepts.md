---
skill_id: 15cbce4f4e0f
usage_count: 1
last_used: 2026-06-16
---
## Core Concepts

### AnimatePresence contract

Three things must always be true:

1. `AnimatePresence` wraps the conditional
2. The direct child has a `key`
3. The child has an `exit` prop

Miss any one of these and the exit animation silently fails.

### layout vs layoutId

- `layout` — animates the element's own size/position change in place
- `layoutId` — links two separate elements, crossfading between them across renders

Use `layout="position"` on text inside an expanding container to prevent text reflow from animating.