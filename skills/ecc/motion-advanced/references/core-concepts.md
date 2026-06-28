---
skill_id: 15cbce4f4e0f
usage_count: 1
last_used: 2026-06-16
---
## Core Concepts

### useMotionValue + useTransform

Reactive computation without re-renders:

```tsx
const x = useMotionValue(0)
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0])
// opacity updates every frame as x changes — no setState, no re-render
```

### useAnimate

Returns `[scope, animate]`. The scope ref must be attached to a DOM element.
`animate()` calls are interrupt-safe — calling mid-flight cancels the previous run.

```tsx
const [scope, animate] = useAnimate()

async function play() {
  await animate(".step-1", { opacity: 1 }, { duration: 0.3 })
  await animate(".step-2", { x: 0 },       { duration: 0.4 })
        animate(".step-3", { scale: 1 },    { duration: 0.25 })  // fire and forget
}

return <div ref={scope}>...</div>
```