
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Path Ayirici |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# KIRILMA KOŞULU 7 — Evrensel Path Ayırıcı

**Tetikleyici:** Sabit `\` veya `/` içeren dosya yolu

**Kırılma:** Windows `\` kullanır, Linux `/` kullanır. Sabit ayırıcı çapraz platformda kırılır.

**Çözüm:**
```python
from pathlib import Path
yol = Path("skills") / "alt_dizin" / "dosya.md"

# veya
import os
yol = os.path.join("skills", "alt_dizin", "dosya.md")
```
