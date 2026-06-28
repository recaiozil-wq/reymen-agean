
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flox Environments_References_Good Return From Hook Don T Exit |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# GOOD — return from hook, don't exit
[hook]
on-activate = """
  if [ ! -f config.json ]; then
    echo "Missing config — run setup first"
    return 1
  fi
"""
```

### Storing Secrets in Manifest

```toml