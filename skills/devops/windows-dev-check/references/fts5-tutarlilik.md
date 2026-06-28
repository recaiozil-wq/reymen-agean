---
skill_id: 8644f149ea8f
usage_count: 1
last_used: 2026-06-16
---
# KIRILMA KOŞULU 4 — FTS5 Tutarsızlığı

**Tetikleyici:** `migrate_skills.py`, `beceri_kristallestir()`

**Kırılma:** Migration betiği dosyaya frontmatter ekler ama FTS5 index'teki `icerik` alanı güncellenmezse aramalar eski içerikte çalışır.

**Çözüm:**
```python
con.execute("UPDATE beceriler SET icerik=? WHERE kaynak=?", (yeni_icerik, kaynak))
```
