---
skill_id: 95f5a6e4c8b7
usage_count: 1
last_used: 2026-06-16
---
## Decision Guidance

### Choosing a duration

| Token | Use when |
| --------- | -------------------------------------------- |
| `instant` | Tooltip show/hide, focus ring, badge update |
| `fast` | Button feedback, icon swap, chip toggle |
| `normal` | Modal open, card expand, page element enter |
| `slow` | Hero entrance, full-page transition |
| `crawl` | Deliberate storytelling; use sparingly |

### Choosing a spring

| Preset | Use when |
| --------- | ------------------------------------------ |
| `snappy` | Default UI — buttons, chips, nav items |
| `gentle` | Cards, modals, panels landing softly |
| `bouncy` | Playful moments — empty states, onboarding |
| `instant` | Tooltips, popovers, dropdowns |
| `release` | Drag release — natural physics feel |

### When to disable animation entirely

Disable (make `shouldAnimate()` return `false`) when:

- `prefersReduced` is `true`
- `isLowEnd` is `true` and the animation is non-essential
- The element is off-screen and will never enter the viewport
- The animation is purely decorative with no UX purpose