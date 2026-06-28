
> **Kategori:** Yaratici

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Creative_Claude Design_References_React Guidance For Standalone Html |
| **Nerede?** | Yaratici/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## React Guidance for Standalone HTML

Use plain HTML/CSS/JS by default.

Use React only when:

- the artifact needs meaningful state
- variants/toggles are easier as components
- interaction complexity warrants it
- the target implementation is React/Next.js and fidelity matters

If using React from CDN in standalone HTML:

- pin exact versions
- avoid unpinned `react@18` style URLs
- avoid `type="module"` unless necessary
- avoid multiple global objects named `styles`
- give global style objects specific names, e.g. `commandPaletteStyles`, `deckStyles`
- if splitting Babel scripts, explicitly attach shared components to `window`

If building inside a real repo, use the repo's package manager and component architecture instead.