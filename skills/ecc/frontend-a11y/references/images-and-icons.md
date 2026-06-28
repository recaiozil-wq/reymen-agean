---
skill_id: 0de371305388
usage_count: 1
last_used: 2026-06-16
---
## Images and Icons

```tsx
// BAD: decorative icon announced as unlabeled image
<img src="/icon.svg" />

// GOOD: decorative image hidden from screen readers
<img src="/decoration.png" alt="" aria-hidden="true" />

// GOOD: meaningful image with descriptive alt text
<img src="/chart.png" alt="Monthly revenue increased 23% from January to March" />

// GOOD: icon button with accessible label
<button aria-label="Delete item">
  <TrashIcon aria-hidden="true" />
</button>
```