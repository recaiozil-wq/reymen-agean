---
name: ecc_motion-advanced_references_anti-patterns
description: Anti-Patterns
title: "Ecc Motion Advanced References Anti Patterns"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_motion-advanced_references_anti-patterns.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Anti-Patterns

| Anti-pattern | Rule violated | Fix |
| ---------------------------------------------- | ------- | ------------------------------------------------ |
| `drag` tested only on desktop | Rule 1 | Test on touch emulator and real device |
| `animate={{ repeat: Infinity }}` with no pause | Rule 2 | Add `visibilitychange` listener |
| `onDragEnd` checking only offset, not velocity | Rule 3 | Check both `info.offset` and `info.velocity` |
| `animate(scope, ...)` before `useEffect` | Rule 4 | Call `animate()` only after mount |
| `const x = new MotionValue(0)` in render | Rule 5 | Use `const x = useMotionValue(0)` |
| `transition={{ duration: 1.2 }}` inline | Rule 6 | Use `motionTokens.duration.crawl` |
| `useEffect` without cleanup | Rule 7 | Return `removeEventListener` / `controls.stop` |
| SVG morph between paths with different commands | Rule 8 | Normalize path commands before animating |
