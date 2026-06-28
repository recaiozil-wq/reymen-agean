# -*- coding: utf-8 -*-
"""gateway/platforms/signal.py — Signal Platformu.

signal-cli (komut satiri) uzerinden Signal mesaji gonderir.
"""

import os
import subprocess
import sys
import logging
logger = logging.getLogger(__name__)


def _signal_cli_bul() -> str:
    adaylar = ["signal-cli", "signal-cli.exe"]
    for a in adaylar:
        try:
            r = subprocess.run(["where", a] if sys.platform == "win32" else ["which", a],
                               capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip().split("\n")[0]
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
    return ""


def baslat():
    pass


def durdur():
    pass


def ping() -> bool:
    """signal-cli erişilebilir mi kontrol et."""
    return bool(_signal_cli_bul())


def durum_al() -> dict:
    """Signal bağlantı durumunu döndür.

    Returns:
        dict: {"durum": ..., "signal_cli": ..., "numara": bool}
    """
    numara = os.environ.get("SIGNAL_NUMBER", "")
    cli = _signal_cli_bul()
    return {
        "durum": "hazir" if cli and numara else "yapilandirilmamis",
        "signal_cli": cli,
        "numara": bool(numara),
    }


def parse_message(raw: dict) -> dict:
    """Signal mesajını normalize et."""
    if not isinstance(raw, dict):
        return {"gonderen": "", "metin": "", "platform": "signal"}
    return {
        "gonderen": str(raw.get("source", "")),
        "metin": str(raw.get("message", "")),
        "platform": "signal",
        "ham": raw,
    }


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Signal uzerinden mesaj gonder.

    Args:
        hedef: Telefon numarasi (uluslararasi formatta, +90xxxxxxxxx)
        mesaj: Gonderilecek metin
    """
    signal_cli = _signal_cli_bul()
    if not signal_cli:
        return "[Signal]: signal-cli bulunamadi."

    numara = os.environ.get("SIGNAL_NUMBER", "")
    if not numara:
        return "[Signal]: SIGNAL_NUMBER ayarlanmamis."

    try:
        r = subprocess.run(
            [signal_cli, "-u", numara, "send", "-m", mesaj, hedef],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            return "[Signal]: Mesaj gonderildi."
        return f"[Signal]: Hata: {r.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return "[Signal]: Zaman asimi."
    except Exception as e:
        return f"[Signal]: Hata: {e}"



