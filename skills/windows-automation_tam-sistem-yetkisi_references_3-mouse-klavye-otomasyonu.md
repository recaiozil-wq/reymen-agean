
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_3 Mouse Klavye Otomasyonu |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## 3. Mouse / Klavye Otomasyonu

### Kurulum (bir kez)

```bash
pip install pyautogui pillow
```

### Mouse tıklama ve hareket

```python
import pyautogui
import time

pyautogui.FAILSAFE = True   # Sol üst köşeye mouse giderse dur (guvenlik)
pyautogui.PAUSE   = 0.3     # Her eylem arası bekleme (saniye)