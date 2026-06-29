---
name: ecc_motion-advanced_references_core-concepts
description: Core Concepts
title: "Ecc Motion Advanced References Core Concepts"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_motion-advanced_references_core-concepts.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

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
