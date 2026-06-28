
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flox Environments_References_Debugging |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Debugging

```bash
flox list -c                      # Show raw manifest
flox activate -- which python     # Check which binary resolves
flox activate -- env | grep FLOX  # See Flox environment variables
flox search <package> --all       # Broader package search (case-sensitive)
```

**Common issues:**
- **Package not found:** Search is case-sensitive — try `flox search --all`
- **File conflicts between packages:** Add `priority` to the package that should win
- **Hook failures:** Use `return` not `exit`; guard with `${FLOX_ENV_CACHE:-}`
- **Stale dependencies:** Delete the `$FLOX_ENV_CACHE/.deps_installed` flag file