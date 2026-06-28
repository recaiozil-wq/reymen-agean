
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Fts5 Tutarlilik |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# KIRILMA KOŞULU 4 — FTS5 Tutarsızlığı

**Tetikleyici:** `migrate_skills.py`, `beceri_kristallestir()`

**Kırılma:** Migration betiği dosyaya frontmatter ekler ama FTS5 index'teki `icerik` alanı güncellenmezse aramalar eski içerikte çalışır.

**Çözüm:**
```python
con.execute("UPDATE beceriler SET icerik=? WHERE kaynak=?", (yeni_icerik, kaynak))
```
