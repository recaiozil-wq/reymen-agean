
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Crlf Normalizasyon |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# KIRILMA KOŞULU 1 — CRLF Normalizasyonu

**Tetikleyici:** `write_text()`, `Path.write_text()`, `open("w")`

**Kırılma:** Windows `\r\n` (CRLF) üretir. `_frontmatter_parse`, `_frontmatter_guncelle` gibi fonksiyonlar `\n` (LF) bekler.

**Çözüm:**
```python
icerik = dosya.read_text(encoding="utf-8")
icerik = icerik.replace("\r\n", "\n")  # normalize
meta = _frontmatter_parse(icerik)      # sonra parse
```

**Nerede kullanılır:** `yetenek_fabrikasi.py` (_frontmatter_parse, _frontmatter_guncelle, yetenek_test_et), `closed_learning_loop.py` (_md_ayristir)
