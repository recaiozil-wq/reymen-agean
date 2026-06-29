
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Frontend A11Y_References_Anti Patterns |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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