# -*- coding: utf-8 -*-
"""
discord_bot.py — Discord Bot Gateway Wrapper.

discord.py kullanarak Discord'a mesaj gonderir.
Token .env dosyasindaki DISCORD_BOT_TOKEN degiskeninden okunur.

Kullanim:
    from reymen.ag.discord_bot import discord_gonder, motor_kaydet

    # Dogrudan kullanim
    sonuc = discord_gonder("Merhaba Discord!", kanal_id="123456789")

Kosullar:
    pip install discord.py python-dotenv
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Sabitler ────────────────────────────────────────────────────────────
ORTAM_DEGISKENI_TOKEN = "DISCORD_BOT_TOKEN"
ORTAM_DEGISKENI_KANAL = "DISCORD_CHANNEL_ID"
VARSAYILAN_TIMEOUT = 10


# ═══════════════════════════════════════════════════════════════════════
#  Yardimci: .env yukle
# ═══════════════════════════════════════════════════════════════════════


def _dotenv_yukle() -> None:
    """python-dotenv varsa .env dosyasini yukler."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass  # dotenv yoksa env degiskenlerini oldugu gibi kullan


def _token_al() -> str:
    """DISCORD_BOT_TOKEN ortam degiskenini dondurur."""
    _dotenv_yukle()
    token = os.environ.get(ORTAM_DEGISKENI_TOKEN, "").strip()
    return token


def _kanal_id_al() -> str:
    """Varsayilan kanal ID'sini ortam degiskeninden alir."""
    return os.environ.get(ORTAM_DEGISKENI_KANAL, "").strip()


# ═══════════════════════════════════════════════════════════════════════
#  Discord Mesaj Gonderme (sync wrapper)
# ═══════════════════════════════════════════════════════════════════════


def discord_gonder(
    mesaj: str,
    kanal_id: Optional[str] = None,
    token: Optional[str] = None,
) -> dict[str, Any]:
    """Discord kanalina mesaj gonderir.

    Args:
        mesaj: Gonderilecek metin (max 2000 karakter, Discord siniri)
        kanal_id: Hedef kanal ID'si (bos birakilirsa ortam degiskeninden alinir)
        token: Discord bot token'i (bos birakilirsa .env'den alinir)

    Returns:
        {"basarili": True/False, "hata": "...", ...}
    """
    try:
        token = token or _token_al()
        if not token:
            return {
                "basarili": False,
                "hata": f"{ORTAM_DEGISKENI_TOKEN} bulunamadi (.env veya ortam)",
            }

        kanal = kanal_id or _kanal_id_al()
        if not kanal:
            return {
                "basarili": False,
                "hata": (
                    f"Hedef kanal ID'si gerekli (parametre veya "
                    f"{ORTAM_DEGISKENI_KANAL} ortam degiskeni)"
                ),
            }

        # Discord API'ye REST ile mesaj gonder
        import urllib.request
        import json

        url = f"https://discord.com/api/v10/channels/{kanal}/messages"
        body = json.dumps({"content": mesaj[:2000]}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
                "User-Agent": "DiscordBot (ReYMeN, 1.0)",
            },
        )

        with urllib.request.urlopen(req, timeout=VARSAYILAN_TIMEOUT) as r:
            yanit = json.loads(r.read())

        logger.info("[Discord] Mesaj gonderildi -> kanal=%s", kanal)
        return {"basarili": True, "kanal_id": kanal, "mesaj_id": yanit.get("id")}

    except Exception as e:
        hata = str(e)
        logger.error("[Discord] Gonderme hatasi: %s", hata)
        return {"basarili": False, "hata": hata}


# ═══════════════════════════════════════════════════════════════════════
#  Motor Kayit (plugin sistemi)
# ═══════════════════════════════════════════════════════════════════════


def motor_kaydet(motor: Any) -> None:
    """Discord gonderici aracini motor systemine kaydeder.

    Ornek kullanim:
        >>> motor_kaydet(motor)
        >>> # motor artik DISCORD_GONDER aracina sahip
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "DISCORD_GONDER",
        lambda mesaj="", kanal_id="": discord_gonder(mesaj, kanal_id),
        "Discord kanalina mesaj gonder (mesaj, kanal_id: opsiyonel — bos=env'den)",
    )


# ═══════════════════════════════════════════════════════════════════════
#  Ayri bir process olarak calistirma (DiscordAdapter icin)
# ═══════════════════════════════════════════════════════════════════════


def main() -> None:
    """Discord bot'unu ayri process olarak calistir.

    DiscordAdapter (gateway_manager.py) tarafindan subprocess olarak
    cagrilir. .ReYMeN/discord_status.json dosyasi uzerinden iletisim kurar.
    """
    import json
    import time
    from pathlib import Path

    proje_koku = Path(__file__).resolve().parent.parent.parent.parent
    durum_dosyasi = proje_koku / ".ReYMeN" / "discord_status.json"
    durum_dosyasi.parent.mkdir(parents=True, exist_ok=True)

    logger.info("[DiscordBot] Main loop basladi (pid=%d)", os.getpid())

    try:
        while True:
            # Durum dosyasini kontrol et
            if durum_dosyasi.exists():
                try:
                    data = json.loads(durum_dosyasi.read_text(encoding="utf-8"))
                    bekleyen = data.pop("_sira_bekleyen_mesaj", None)
                    if bekleyen:
                        sonuc = discord_gonder(
                            bekleyen.get("mesaj", ""),
                            kanal_id=bekleyen.get("kanal_id"),
                        )
                        data["_son_gonderme"] = sonuc
                        data["_son_guncelleme"] = time.time()
                        durum_dosyasi.write_text(
                            json.dumps(data, indent=2, ensure_ascii=False),
                            encoding="utf-8",
                        )
                except Exception as _e:
                    logger.warning("[DiscordBot] Durum okuma hatasi: %s", _e)

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("[DiscordBot] Kapatiliyor...")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
