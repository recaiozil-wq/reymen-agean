---
skill_id: 95f5a6e4c8b7
usage_count: 1
last_used: 2026-06-16
---
## Decision Guidance

### Choosing the right advanced API

| Scenario | API |
| ------------------------------ | -------------------------------- |
| Drag with physics on release | `drag` + `dragTransition: springs.release` |
| Ordered drag-to-reorder list | `Reorder.Group` + `Reorder.Item` |
| Dismiss on drag offset | `drag="y"` + `onDragEnd` offset check |
| Swipe left/right | `drag="x"` + `onDragEnd` offset check |
| Long press | `useLongPress` hook |
| Value smoothed over time | `useSpring` |
| Value derived from another | `useTransform` |
| Multi-step sequence | `useAnimate` with `async/await` |
| One-shot imperative animation | `animate()` from `motion` |
| Text entering word by word | Stagger on `inline-block` spans |
| SVG drawing on | `pathLength` 0 → 1 |
| SVG morph | `d` attribute tween (equal commands) |
| Circular progress | `strokeDashoffset` tween |

### When to use `useSpring` vs a spring transition

| | `useSpring` | `transition: springs.*` |
| -------------- | ---------------------------------------- | ----------------------- |
| Use for | Cursor follower, pointer-tracked values | Discrete state changes |
| Updates | Continuous, on every frame | Triggered by state change |
| Interrupt | Smooth — physics picks up from velocity | Restarts from current value |