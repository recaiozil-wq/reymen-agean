
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flutter Dart Code Review_References_14 Dependency Injection |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## 14. Dependency Injection

### Principles (apply to any DI approach):
- [ ] Classes depend on abstractions (interfaces), not concrete implementations at layer boundaries
- [ ] Dependencies provided externally via constructor, DI framework, or provider graph — not created internally
- [ ] Registration distinguishes lifetime: singleton vs factory vs lazy singleton
- [ ] Environment-specific bindings (dev/staging/prod) use configuration, not runtime `if` checks
- [ ] No circular dependencies in the DI graph
- [ ] Service locator calls (if used) are not scattered throughout business logic

---