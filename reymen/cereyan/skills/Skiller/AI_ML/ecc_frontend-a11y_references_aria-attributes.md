
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Frontend A11Y_References_Aria Attributes |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## ARIA Attributes

Use ARIA only when native HTML semantics are insufficient. Wrong ARIA is worse than no ARIA.

### aria-label vs aria-labelledby

```tsx
// aria-label: inline string label — use when no visible label text exists
<button aria-label="Close modal">
  <XIcon />
</button>

// aria-labelledby: references another element's text — use when a visible label exists
<section aria-labelledby="section-title">
  <h2 id="section-title">Recent Orders</h2>
  {/* content */}
</section>
```

### aria-describedby

```tsx
// Provides supplementary description beyond the label
<button
  aria-describedby="delete-warning"
  onClick={handleDelete}
> Delete account
</button>
<p id="delete-warning">This action cannot be undone.</p>
```

### aria-live for Dynamic Content

```tsx
// Use aria-live to announce content that updates without a page reload
// polite: waits for user to finish current action before announcing
// assertive: interrupts immediately — use only for urgent errors

export function StatusMessage({ message, isError }: { message: string; isError?: boolean }) {
  return (
    <div role="status" aria-live={isError ? 'assertive' : 'polite'} aria-atomic="true">
      {message}
    </div>
  );
}
```

### aria-expanded and aria-controls

```tsx
export function Accordion({ title, children }: { title: string; children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const contentId = useId();

  return (
    <div>
      <button aria-expanded={isOpen} aria-controls={contentId} onClick={() => setIsOpen(prev => !prev)}>
        {title}
      </button>
      <div id={contentId} hidden={!isOpen}>
        {children}
      </div>
    </div>
  );
}
```