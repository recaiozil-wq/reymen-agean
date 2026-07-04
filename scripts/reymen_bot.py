#!/usr/bin/env python3
"""
reymen_bot.py — ReYMeN Telegram Bot (Hermes Gateway'siz)

Kullanim:
    python reymen_bot.py                    # Varsayilan bot
    python reymen_bot.py --bot pasa_38     # Belirli bot
    python reymen_bot.py --list            # Botlari listele

Not: Bu dosya Hermes Agent'ten bagimsiz calisir.
     Apache 2.0 Lisansi — github.com/NousResearch/hermes-agent
"""

import os
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("reymen_bot")

# Proje koku
PROJE = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJE))

# .env yukle
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def botlari_listele():
    """durum.json'dan botlari oku"""
    dj = PROJE / "durum.json"
    if not dj.exists():
        print("durum.json bulunamadi")
        return
    with open(dj) as f:
        d = json.load(f)
    for ad, bilgi in d.get("botlar", {}).items():
        profil = bilgi.get("profil", "?")
        bot_adi = bilgi.get("bot_adi", "?")
        env_key = f"TELEGRAM_BOT_TOKEN_{ad.upper()}"
        token = os.getenv(env_key, "-")
        print(
            f"  {ad:15s} {bot_adi:20s} profil={profil:10s} token={'✅' if token != '-' else '❌'}"
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ReYMeN Telegram Bot (bagimsiz)")
    parser.add_argument(
        "--bot", default="pasa_38", help="Bot adi (pasa_38, kiral38, reymen)"
    )
    parser.add_argument("--list", action="store_true", help="Botlari listele")
    args = parser.parse_args()

    if args.list:
        print("Kullanilabilir botlar:")
        botlari_listele()
        return

    # Bot token
    env_key = f"TELEGRAM_BOT_TOKEN_{args.bot.upper()}"
    token = os.getenv(env_key) or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Token bulunamadi. .env dosyasina %s ekleyin", env_key)
        sys.exit(1)

    # PTB modunda baslat
    os.environ["HERMES_GATEWAY"] = "ptb"
    os.environ["BOT_TOKEN"] = token

    logger.info("ReYMeN Bot baslatiliyor: %s (PTB mod, Gateway'siz)", args.bot)

    # telegram_bot.py'yi calistir
    bot_modul = PROJE / "reymen" / "ag" / "telegram_bot.py"
    if not bot_modul.exists():
        logger.error("telegram_bot.py bulunamadi: %s", bot_modul)
        sys.exit(1)

    # Dogrudan main'i import et ve calistir
    sys.argv = [str(bot_modul)]
    with open(bot_modul) as f:
        exec(f.read(), {"__name__": "__main__", "__file__": str(bot_modul)})


if __name__ == "__main__":
    main()
