
> **Kategori:** Egitim

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Note Taking_Obsidian Vault Maintenance_References_T M Dosyalar Alt Klas R Yoluyla Birlikte Md Olmadan |
| **Nerede?** | Egitim/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# TÜM dosyalar (alt klasör yoluyla birlikte, .md olmadan)
existing = set()
for root, dirs, files in os.walk(VAULT):
    for f in files:
        if f.endswith('.md'):
            rel = os.path.relpath(os.path.join(root, f), VAULT).replace('\\', '/').replace('.md', '')
            existing.add(rel)
            name = f.replace('.md', '')
            existing.add(name)