
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flutter Dart Code Review_References_8 Platform Specific Concerns |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## 8. Platform-Specific Concerns

### iOS/Android differences:
- [ ] Platform-adaptive widgets used where appropriate
- [ ] Back navigation handled correctly (Android back button, iOS swipe-to-go-back)
- [ ] Status bar and safe area handled via `SafeArea` widget
- [ ] Platform-specific permissions declared in `AndroidManifest.xml` and `Info.plist`

### Responsive design:
- [ ] `LayoutBuilder` or `MediaQuery` used for responsive layouts
- [ ] Breakpoints defined consistently (phone, tablet, desktop)
- [ ] Text doesn't overflow on small screens — use `Flexible`, `Expanded`, `FittedBox`
- [ ] Landscape orientation tested or explicitly locked
- [ ] Web-specific: mouse/keyboard interactions supported, hover states present

---