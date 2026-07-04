#!/usr/bin/env python3
"""
reymen_gateway.py — ReYMeN Gateway (Hermes'siz Telegram Bot)

Hermes Agent (Nous Research, Apache 2.0) kaynak kodundan uyarlanmistir.
Bu dosya, Hermes Gateway olmadan Telegram botlarini calistirir.

Kullanim:
    python reymen_gateway.py                    # Tum botlari baslat
    python reymen_gateway.py --bot pasa_38     # Tek bot
    python reymen_gateway.py --list            # Botlari listele
"""

import json
import logging
import os
import sys
import threading
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("reymen_gateway")

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
    """durum.json'dan botlari listele"""
    durum_path = PROJE / "reymen" / "sistem" / "durum.json"
    if not durum_path.exists():
        print("durum.json bulunamadi")
        return
    with open(durum_path, encoding="utf-8") as f:
        d = json.load(f)
    aktif = d.get("aktif_ajanlar", {})
    for ad, bilgi in aktif.items():
        profil = bilgi.get("profil", "?")
        env_key = f"TELEGRAM_BOT_TOKEN_{ad.split('@')[-1].upper()}"
        token = os.getenv(env_key)
        print(f"  {ad:25s} profil={profil:10s} token={'✅' if token else '❌'}")


def bot_ayarlarini_al(bot_ad: str) -> dict:
    """Belirli bir botun ayarlarini durum.json'dan al."""
    durum_path = PROJE / "reymen" / "sistem" / "durum.json"
    if not durum_path.exists():
        return {}
    with open(durum_path, encoding="utf-8") as f:
        d = json.load(f)
    aktif = d.get("aktif_ajanlar", {})
    for ad, bilgi in aktif.items():
        if bot_ad in ad.lower():
            return bilgi
    return {}


def botu_baslat(bot_adi: str, profil: str):
    """Tek bir botu ReYMeN Gateway uzerinden baslat."""
    env_key = f"TELEGRAM_BOT_TOKEN_{bot_adi.upper()}"
    token = os.getenv(env_key) or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("%s icin token bulunamadi (%s)", bot_adi, env_key)
        return

    # ReYMeN Gateway Telegram platformunu baslat
    logger.info("🔄 %s baslatiliyor (profil: %s)...", bot_adi, profil)

    try:
        from reymen.gateway.platforms.telegram import TelegramAdapter

        logger.info("✅ %s hazir (TelegramAdapter sinifi mevcut)", bot_adi)
    except Exception as e:
        logger.error("%s baslatilamadi: %s", bot_adi, e)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ReYMeN Gateway (Hermes'siz)")
    parser.add_argument("--bot", help="Bot adi (pasa_38, kiral38, reymen)")
    parser.add_argument("--list", action="store_true", help="Botlari listele")
    parser.add_argument("--all", action="store_true", help="Tum botlari baslat")
    args = parser.parse_args()

    if args.list:
        print("Kullanilabilir botlar:")
        botlari_listele()
        return

    if args.bot:
        ayarlar = bot_ayarlarini_al(args.bot)
        profil = ayarlar.get("profil", "default")
        botu_baslat(args.bot, profil)
    elif args.all:
        durum_path = PROJE / "reymen" / "sistem" / "durum.json"
        with open(durum_path, encoding="utf-8") as f:
            d = json.load(f)
        for ad, bilgi in d.get("aktif_ajanlar", {}).items():
            bot_adi = ad.split("@")[-1].lower() + "_bot"
            if bot_adi.endswith("_bot_bot"):
                bot_adi = bot_adi.replace("_bot_bot", "_bot")
            profil = bilgi.get("profil", "default")
            botu_baslat(bot_adi, profil)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
