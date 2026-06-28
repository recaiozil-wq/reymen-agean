
> **Kategori:** Egitim

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Note Taking_Obsidian Vault Maintenance_References_Kategori Ad Alfabetik |
| **Nerede?** | Egitim/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Kategori Adı (alfabetik)

### A
- [[path/to/NotAdı|NotAdı]]
- [[path/to/DigerNot|DiğerNot]]

### B
- [[path/to/BaskaNot|BaşkaNot]]
```

**Orphan tespit scripti:**
```python
all_links = set()
for md in all_md:
    content = md.read_text(encoding="utf-8", errors="replace")
    found = re.findall(r'\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]', content)
    for link in found:
        all_links.add(link.split("/")[-1])

orphans = []
for md in all_md:
    stem = md.stem
    if stem.startswith('_'): continue  # index dosyaları
    if stem in ('daily', 'tasks', 'kanban'): continue  # Obsidian özel
    if stem not in all_links:
        orphans.append(md)
```

### 4. Toplu Etiket Ekleme

Frontmatter'a `tags:` alanı ekle. Etiket politikası:

```
#hermes            → kök Hermes notları
#hermes #skill     → skill notları
#hermes #knowledge → Knowledge/ altı (taşınmış notlar)
#hermes #skill #kategori → kategori bazlı
```

Dotayı direkt `write_file` ile baştan yaz. `patch` riskli çünkü önceki içerik tutarsız olabilir.

### 5. Doğrulama

Düzeltme bittikten sonra aynı script 2 kere daha çalıştırılır:
- Kalan kırık link sayısını raporla
- Kalan orphan sayısını raporla
- Toplam dosya sayısını raporla

Kalan 0-5 kırık link (eğitim amaçlı örnekler hariç) kabul edilebilir.