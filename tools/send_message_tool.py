# -*- coding: utf-8 -*-
"""send_message_tool.py — Mesaj Gonderme Araci.

Telegram, terminal ve diger kanallara mesaj gonderme.
"""

import os
import subprocess
from pathlib import Path


def telegram_gonder(mesaj: str, token: str = "", chat_id: str = "") -> str:
    """Telegram'a mesaj gonder.

    Args:
        mesaj: Gonderilecek mesaj
        token: Bot token (bos = .env'den al)
        chat_id: Hedef chat ID (bos = .env'den al)

    Returns:
        Durum mesaji
    """
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token or token.startswith("***"):
        return "[Telegram]: Token ayarlanmamis."
    if not chat_id:
        return "[Telegram]: Chat ID ayarlanmamis."

    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": mesaj[:4000]}, timeout=10)
        if r.status_code == 200:
            return f"[Telegram]: Mesaj gonderildi."
        return f"[Telegram]: Hata {r.status_code}"
    except ImportError:
        return "[Telegram]: requests kutuphanesi yok."
    except Exception as e:
        return f"[Telegram]: Hata: {e}"


def terminal_gonder(mesaj: str) -> str:
    """Terminale mesaj yaz."""
    print(f"\n[ReYMeN Mesaj]: {mesaj}\n")
    return "[Terminal]: Mesaj yazdirildi."


def mesaj_gonder(kanal: str, mesaj: str, **kwargs) -> str:
    """Genel mesaj gonderme fonksiyonu.

    Args:
        kanal: "telegram", "terminal"
        mesaj: Gonderilecek metin

    Returns:
        Durum mesaji
    """
    if kanal == "telegram":
        return telegram_gonder(mesaj, **kwargs)
    elif kanal == "terminal":
        return terminal_gonder(mesaj)
    return f"[Hata]: Bilinmeyen kanal '{kanal}'."


if __name__ == "__main__":
    print(terminal_gonder("test mesaji"))
