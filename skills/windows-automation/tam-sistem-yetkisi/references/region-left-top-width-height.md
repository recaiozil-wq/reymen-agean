---
skill_id: 53daccd3be9c
usage_count: 1
last_used: 2026-06-16
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