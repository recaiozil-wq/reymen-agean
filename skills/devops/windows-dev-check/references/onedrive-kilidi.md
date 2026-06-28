---
skill_id: 32907cc185b0
usage_count: 1
last_used: 2026-06-16
---
# KIRILMA KOŞULU 2 — OneDrive Dosya Kilidi

**Tetikleyici:** `shutil.rmtree()`, `os.unlink()`, `Path.unlink()`, `os.remove()`

**Kırılma:** OneDrive senkronizasyonu dosyayı kilitler → `PermissionError: [WinError 5]`

**Çözüm:**
```python
import shutil
from datetime import datetime

try:
    shutil.rmtree(hedef_dizin)
except PermissionError:
    # Zaman damgalı yedek
    yedek = f"{hedef_dizin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree(kaynak, yedek)
```

**Nerede:** `migrate_skills.py` (yedek_al fonksiyonu)
