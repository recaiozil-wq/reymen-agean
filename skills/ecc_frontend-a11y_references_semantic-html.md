
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Frontend A11Y_References_Semantic Html |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Semantic HTML

Use the element that matches the intent. Screen readers and keyboard users depend on native semantics.

```tsx
// BAD: div has no role, no keyboard support, no accessible name
<div onClick={handleClick}>Submit</div>

// GOOD: button is focusable, activates on Enter/Space, announces as "button"
<button type="button" onClick={handleClick}>Submit</button>
```

```tsx
// BAD: non-semantic navigation
<div onClick={() => navigate('/home')}>Home</div>

// GOOD: anchor supports right-click, middle-click, and keyboard navigation
<a href="/home">Home</a>
```

```tsx
// BAD: heading hierarchy skipped (h1 to h4)
<h1>Dashboard</h1>
<h4>Recent Activity</h4>

// GOOD: sequential heading levels
<h1>Dashboard</h1>
<h2>Recent Activity</h2>
```