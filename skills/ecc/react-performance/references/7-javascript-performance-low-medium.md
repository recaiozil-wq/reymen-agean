---
skill_id: 54b787f500f2
usage_count: 1
last_used: 2026-06-16
---
## 7. JavaScript Performance (LOW-MEDIUM)

- **Batch DOM/CSS changes** — apply via class swap or `cssText`, not property-by-property
- **`Map` for repeated lookups** — `O(1)` vs `O(n)` linear scan
- **Cache property access in loops** — `const len = arr.length`
- **Memoize pure functions** — module-level `Map<key, result>`
- **Cache `localStorage` reads** — sync API; one read per render
- **Combine `filter().map()` into one pass** — `flatMap` or single `for`
- **Check array length first** before expensive comparisons
- **Early return** from functions
- **Hoist RegExp** out of loops — compilation is not free
- **Loop for min/max** instead of `sort()` — `O(n)` vs `O(n log n)`
- **`Set`/`Map` for membership** — `O(1)` vs `Array.includes` `O(n)`
- **`toSorted()` over mutation** when immutability matters
- **`flatMap` to map and filter in one pass**
- **`requestIdleCallback`** for non-critical work