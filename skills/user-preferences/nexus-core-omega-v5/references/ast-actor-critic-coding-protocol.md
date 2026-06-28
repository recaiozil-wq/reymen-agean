---
skill_id: 9db4b152ae2c
usage_count: 1
last_used: 2026-06-16
---
## AST-ACTOR-CRITIC (Coding Protocol)

**Activation (v5.0 fix):**
- L99 active + code task → AST-ACTOR-CRITIC runs automatically alongside L99
- ARTIFACTS active + code output → AST-ACTOR-CRITIC runs in parallel
- Neither → AUTOPSY + L99 handles code; AST protocol applies to code block

1. **AST MENTAL ISOLATION:** Analyse logical syntax tree before writing. Isolate target function and scope only.

2. **ACTOR MODEL — Memory-Friendly:**
   - No massive lists loading all data at once
   - Use `yield` without exception
   - Lazy loading is the default standard

3. **CRITIC MODEL — Memory Leak:**
   - Watch for circular references
   - Use `weakref` instead of `dict` for caching
   - Write with `__del__` and GC logic in mind

4. After every code block: "Critic Note" — one sentence on why memory usage is safe.

5. **JS/TS PROTOCOL:**
   - AbortController on every async/await chain
   - Generator-based iterators over Array.from()
   - WeakMap / WeakRef for caching
   - After every async function: Critic Note on memory and cancellation safety

---