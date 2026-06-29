
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flox Environments_References_Teammates Just Run |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Teammates just run:
git clone <repo> && cd <repo> && flox activate
```

For reusable base environments across projects, push to FloxHub:

```bash
flox push                         # Push environment to FloxHub
flox activate -r owner/env-name   # Activate remote environment anywhere
```

Compose environments with `[include]`:

```toml
[include]
base.floxhub = "myorg/python-base"

[install]