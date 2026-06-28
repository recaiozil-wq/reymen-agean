---
skill_id: a092b9d26e09
usage_count: 1
last_used: 2026-06-16
---
## 5. ReYMeN .env Dosyası Tam Erişim Haritası

| Dosya | Yol |
|-------|-----|
| Ana .env | `C:\Users\marko\AppData\Local\hermes\.env` |
| config.yaml | `C:\Users\marko\AppData\Local\hermes\config.yaml` |
| hermes-ai .env | `C:\Users\marko\hermes-ai\.env` |
| Auth | `C:\Users\marko\AppData\Local\hermes\auth.json` |

### .env'den belirli değeri oku

```python
import re
from pathlib import Path

def get_env_value(env_path: str, key: str) -> str:
    text = Path(env_path).read_text(encoding="utf-8")
    m = re.search(rf"^{re.escape(key)}\s*=(.+)", text, re.MULTILINE)
    return m.group(1).strip() if m else ""

token = get_env_value(
    r"C:\Users\marko\AppData\Local\hermes\.env",
    "TELEGRAM_BOT_TOKEN"
)
```

---