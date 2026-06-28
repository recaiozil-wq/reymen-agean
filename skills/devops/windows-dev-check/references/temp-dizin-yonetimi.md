---
skill_id: 8ab44a4c436c
usage_count: 1
last_used: 2026-06-16
---
# KIRILMA KOŞULU 5 — Temp Dizin Yönetimi

**Tetikleyici:** `tempfile.TemporaryDirectory`

**Kırılma:** Context manager çıkarken içindeki read-only dosyayı silemez → PermissionError

**Çözüm:**
```python
import tempfile, shutil
tmp = tempfile.mkdtemp()  # TemporaryDirectory YERINE
try:
    yield tmp
finally:
    shutil.rmtree(tmp, ignore_errors=True)  # manuel cleanup
```
