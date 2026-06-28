---
skill_id: 973aba1cf744
usage_count: 1
last_used: 2026-06-16
---
## 7. Accessibility

### Semantic widgets:
- [ ] `Semantics` widget used to provide screen reader labels where automatic labels are insufficient
- [ ] `ExcludeSemantics` used for purely decorative elements
- [ ] `MergeSemantics` used to combine related widgets into a single accessible element
- [ ] Images have `semanticLabel` property set

### Screen reader support:
- [ ] All interactive elements are focusable and have meaningful descriptions
- [ ] Focus order is logical (follows visual reading order)

### Visual accessibility:
- [ ] Contrast ratio >= 4.5:1 for text against background
- [ ] Tappable targets are at least 48x48 pixels
- [ ] Color is not the sole indicator of state (use icons/text alongside)
- [ ] Text scales with system font size settings

### Interaction accessibility:
- [ ] No no-op `onPressed` callbacks — every button does something or is disabled
- [ ] Error fields suggest corrections
- [ ] Context does not change unexpectedly while user is inputting data

---