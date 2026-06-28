
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_4 Ekran G R Nt S Alma |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## 4. Ekran Görüntüsü Alma

### Tüm ekranı yakala

```python
import pyautogui
from datetime import datetime

def screenshot(path: str = None) -> str:
    if not path:
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = rf"C:\Users\marko\Downloads\screenshot_{ts}.png"
    img = pyautogui.screenshot()
    img.save(path)
    print(f"[OK] Ekran goruntüsü: {path}")
    return path

screenshot()
```

### Belirli bölgeyi yakala

```python
import pyautogui