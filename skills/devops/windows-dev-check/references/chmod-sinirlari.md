---
skill_id: 00876e8dc791
usage_count: 1
last_used: 2026-06-16
---
# KIRILMA KOŞULU 6 — Windows chmod Sınırları

**Tetikleyici:** `os.chmod(dosya, stat.S_IRUSR | stat.S_IWUSR)`

**Kırılma:** Windows `S_IRUSR`, `S_IWGRP`, `S_IXOTH` gibi POSIX flag'lerini ya yok sayar ya da hata verir. Yalnızca `S_IWRITE` ve `S_IREAD` çalışır.

**Çözüm:**
```python
os.chmod(dosya, stat.S_IWRITE)   # yazılabilir
os.chmod(dosya, stat.S_IREAD)    # salt okunur
```
