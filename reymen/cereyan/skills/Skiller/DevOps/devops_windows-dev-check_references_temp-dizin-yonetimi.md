
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Temp Dizin Yonetimi |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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
