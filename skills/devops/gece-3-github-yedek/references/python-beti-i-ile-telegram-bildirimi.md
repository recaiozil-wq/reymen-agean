---
skill_id: 785831703470
usage_count: 1
last_used: 2026-06-16
---
# Python betiği ile Telegram bildirimi
import requests, re
from pathlib import Path

env_path = r"C:\Users\marko\AppData\Local\hermes\.env"
raw = Path(env_path).read_bytes()
text = raw.decode("utf-8", errors="replace")

token = ""
for line in text.splitlines():
    if line.startswith("TELEGRAM_BOT_TOKEN="):
        token = line.split("=", 1)[1].strip().strip('"').strip("'")
        break

if token and "***" not in token:
    msg = "✅ Gece yedeği tamam: Skills + Obsidian vault"  # veya hata mesajı
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                  json={"chat_id": "6328823909", "text": msg}, timeout=10)
```