---
skill_id: 5d2dc583a2dd
usage_count: 1
last_used: 2026-06-16
---
# Kullanim:
set_yaml_value(
    r"C:\Users\marko\AppData\Local\hermes\config.yaml",
    ["telegram", "bot_token"],
    "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
)
```

### ReYMeN CLI ile token ayarla

```bash
hermes config set telegram.bot_token <TOKEN>
```

### Hızlı scriptler

- Token yaz: `python scripts/set_telegram_token.py "<YENI_TOKEN>"`
- Token doğrula: `python scripts/verify_telegram_token.py`

### Bot bağlantısını test et

```python
import requests

def test_telegram_bot(token: str) -> dict:
    r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    data = r.json()
    if data.get("ok"):
        bot = data["result"]
        print(f"[OK] Bot baglandi: @{bot['username']} ({bot['first_name']})")
    else:
        print(f"[HATA] {data}")
    return data