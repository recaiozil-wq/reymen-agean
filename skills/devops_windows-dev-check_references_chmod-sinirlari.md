
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Chmod Sinirlari |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# KIRILMA KOŞULU 6 — Windows chmod Sınırları

**Tetikleyici:** `os.chmod(dosya, stat.S_IRUSR | stat.S_IWUSR)`

**Kırılma:** Windows `S_IRUSR`, `S_IWGRP`, `S_IXOTH` gibi POSIX flag'lerini ya yok sayar ya da hata verir. Yalnızca `S_IWRITE` ve `S_IREAD` çalışır.

**Çözüm:**
```python
os.chmod(dosya, stat.S_IWRITE)   # yazılabilir
os.chmod(dosya, stat.S_IREAD)    # salt okunur
```
