---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

```tsx
// BAD: onClick on non-interactive element with no keyboard support
<div onClick={handleClick}>Click me</div>

// BAD: aria-label on a div that has no role
<div aria-label="Navigation">...</div>

// BAD: placeholder used as a substitute for label
<input placeholder="Enter your email" />

// BAD: positive tabIndex creates unpredictable tab order
<button tabIndex={3}>Submit</button>

// BAD: aria-hidden on a focusable element — keyboard users get trapped
<button aria-hidden="true">Open</button>

// BAD: role="button" on div without keyboard handler
<div role="button" onClick={handleClick}>Submit</div>
// Missing: tabIndex={0}, onKeyDown for Enter/Space
```