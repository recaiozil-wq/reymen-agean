
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Onedrive Kilidi |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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
