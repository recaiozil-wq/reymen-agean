---
skill_id: 5bc04eff0d8a
usage_count: 1
last_used: 2026-06-16
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