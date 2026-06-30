"""ai_bot_launcher.py — Proje kökü .env'den okuyup ai_bot baslatir.

TEK KAYNAK: Bu dosya SADECE proje kökündeki .env dosyasini okur.
telegram_bot/.env veya reymen/sistem/.env OKUNMAZ.
"""
import os
import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.resolve()
ENV_DOSYA = PROJE_KOK / ".env"
BOT_AD = os.environ.get("BOT_AD", "")

# .env dosyasini oku (TEK KAYNAK)
env = {}
try:
    with open(ENV_DOSYA, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
except FileNotFoundError:
    print(f"HATA: {ENV_DOSYA} bulunamadi. .env.example'dan kopyala:")
    print(f"  copy {PROJE_KOK / '.env.example'} {ENV_DOSYA}")
    sys.exit(1)

# Env var'lari birlestir
full_env = {**os.environ, **env}
if BOT_AD:
    full_env["BOT_AD"] = BOT_AD

token = full_env.get("BOT_TOKEN") or full_env.get("TELEGRAM_BOT_TOKEN")
if not token or token == "API_KEYINIZI_GIRIN":
    print("HATA: BOT_TOKEN veya TELEGRAM_BOT_TOKEN .env'de ayarli degil!")
    print("  .env dosyasina gecerli bir token girin.")
    sys.exit(1)

ai_bot_py = PROJE_KOK / "telegram_bot" / "ai_bot.py"
subprocess.run([sys.executable or "python", str(ai_bot_py)], env=full_env)
