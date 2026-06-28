---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

| Anti-pattern | Rule violated | Fix |
| -------------------------------------------- | ------- | ------------------------------------------ |
| `AnimatePresence` child missing `key` | Rule 1 | Add stable `key` to the direct child |
| `initial` + `animate` without `exit` | Rule 2 | Always define all three together |
| Page transition without `mode="wait"` | Rule 3 | Add `mode="wait"` to `AnimatePresence` |
| `layout` on a 50-item list | Rule 4 | Use `mode="popLayout"` or explicit transforms |
| `staggerChildren: 0.2` on a 10-item list | Rule 5 | Cap at `0.08–0.10` |
| Modal without focus trap | Rule 6 | Add `focus-trap-react` or Radix Dialog |
| `whileInView` without `viewport={{ once: true }}` | Rule 7 | Repeating entrances distract, not inform |
| `transition={{ duration: 0.3 }}` inline | Rule 8 | Use `motionTokens.duration.normal` |