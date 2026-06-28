---
skill_id: 3164e4b18dd8
usage_count: 1
last_used: 2026-06-16
---
## Checklist

Before submitting any interactive component for review:

- [ ] Every `<input>`, `<select>`, and `<textarea>` has a connected `<label>` via `htmlFor`/`id`
- [ ] Error messages are linked with `aria-describedby` and marked `role="alert"`
- [ ] No `onClick` on `<div>` or `<span>` without `role`, `tabIndex`, and `onKeyDown`
- [ ] Icon-only buttons have `aria-label`
- [ ] Decorative images use `alt=""` and `aria-hidden="true"`
- [ ] Modals restore focus on close (for full focus trapping with Tab/Shift+Tab cycling, use a library like `focus-trap-react`)
- [ ] Dynamic content updates use `aria-live`
- [ ] `prefers-reduced-motion` is respected for animations