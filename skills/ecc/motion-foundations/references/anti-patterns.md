---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

| Anti-pattern | Rule violated | Fix |
| --------------------------------------- | ------- | ------------------------------- |
| `import { motion } from "framer-motion"` | Rule 1 | Use `motion/react` |
| `initial={{ opacity: 0 }}` on SSR component | Rule 2 | Add mount guard |
| Skipping `useReducedMotion` check | Rule 3 | Use `useSafeMotion` hook |
| `animate={{ width: "100%" }}` | Rule 4 | Use `scaleX` transform instead |
| `transition={{ duration: 0.4 }}` inline | Rule 5 | Use `motionTokens.duration.normal` |
| `{ stiffness: 300, damping: 30 }` inline | Rule 6 | Use `springs.snappy` |
| Missing `"use client"` directive | Rule 7 | Add to top of file |
| `navigator.hardwareConcurrency` at module level | Rule 8 | Wrap in `typeof navigator !== "undefined"` |