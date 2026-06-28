---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

- Using `null` or `undefined` as initial signal form field values — use `''`, `0`, or `[]` instead
- Accessing form field state flags without calling the field first: `form.field.valid()` — use `form.field().valid()`
- Starting new forms with older form APIs when the target Angular version supports Signal Forms
- Setting `min`, `max`, `value`, `disabled`, or `readonly` HTML attributes on `[formField]` inputs — define these as schema rules instead
- Calling `inject()` outside an injection context — use `runInInjectionContext` when needed
- Using `effect()` for derived state that should use `computed()`
- Referencing `$parent.$index` in nested `@for` loops — Angular does not support `$parent`; use `let outerIdx = $index` instead