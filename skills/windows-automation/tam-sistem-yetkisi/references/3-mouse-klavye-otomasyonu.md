---
skill_id: d78c1e2da90e
usage_count: 1
last_used: 2026-06-16
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