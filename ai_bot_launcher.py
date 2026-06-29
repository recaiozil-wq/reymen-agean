"""ai_bot_launcher.py — .env okuyup ai_bot baslatir."""
import os
import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.resolve()
ENV_DOSYA = PROJE_KOK / "telegram_bot" / ".env"
BOT_AD = os.environ.get("BOT_AD", "")

# .env dosyasini oku
env = {}
try:
    with open(ENV_DOSYA, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
except FileNotFoundError:
    pass

# Env var'lari birlestir
full_env = {**os.environ, **env}
if "BOT_TOKEN" in os.environ:
    full_env["BOT_TOKEN"] = os.environ["BOT_TOKEN"]
if BOT_AD:
    full_env["BOT_AD"] = BOT_AD

token = full_env.get("BOT_TOKEN") or full_env.get("TELEGRAM_BOT_TOKEN")
if not token:
    print("HATA: BOT_TOKEN veya TELEGRAM_BOT_TOKEN bulunamadi")
    sys.exit(1)

ai_bot_py = PROJE_KOK / "telegram_bot" / "ai_bot.py"
subprocess.run([sys.executable or "python", str(ai_bot_py)], env=full_env)
