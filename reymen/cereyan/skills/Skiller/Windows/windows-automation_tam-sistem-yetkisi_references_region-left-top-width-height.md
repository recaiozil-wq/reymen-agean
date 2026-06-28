
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_Region Left Top Width Height |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# region = (left, top, width, height)
img = pyautogui.screenshot(region=(0, 0, 800, 600))
img.save(r"C:\Users\marko\Downloads\bolge.png")
```

### Ekranı analiz et (PIL ile)

```python
from PIL import Image
import pyautogui

img  = pyautogui.screenshot()
pix  = img.getpixel((500, 300))   # piksel rengi (R, G, B)
print(f"Piksel rengi: {pix}")