"""Token oku ve bot test et."""
import os
import sys
from pathlib import Path

# ReYMeN token
env_path = Path.home() / "AppData/Local/hermes/profiles/reymen/.env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("TELEGRAM_BOT_TOKEN"):
            token = line.split("=", 1)[1].strip().strip("'\"")

# Pasa token
default_env = Path.home() / "AppData/Local/hermes/.env"
pasa_token = ""
if default_env.exists():
    for line in default_env.read_text().splitlines():
        line = line.strip()
        if line.startswith("TELEGRAM_BOT_TOKEN"):
            pasa_token = line.split("=", 1)[1].strip().strip("'\"")

print(f"ReYMeN token: {token[:15]}... (len={len(token)})")
print(f"Pasa token:   {pasa_token[:15]}... (len={len(pasa_token)})")

os.environ["BOT_TOKEN"] = token
os.environ["BOT_AD"] = "@ReYMeN_ReYMeNbot"

from reymen.telegram_bot import ReYMeNTelegramBot
bot = ReYMeNTelegramBot(token=token, bot_ad="test")
print("✅ Bot sinifi basariyla olusturuldu")
