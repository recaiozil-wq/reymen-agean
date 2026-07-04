# -*- coding: utf-8 -*-

"""
whatsapp_gateway.py — WhatsApp Mesaj Gonderme Gateway.

Twilio WhatsApp Business API (HTTP REST) kullanarak mesaj gonderir.
Harici bir kutuphane GEREKTIRMEZ — urllib ile ham HTTP istegi gonderir.

Baglanti bilgileri .env dosyasindaki su degiskenlerden okunur:
  - WHATSAPP_ACCOUNT_SID — Twilio hesap SID'si
  - WHATSAPP_AUTH_TOKEN — Twilio auth token (WHATSAPP_API_KEY da kullanilabilir)
  - WHATSAPP_NUMBER    — Twilio WhatsApp numarasi (whatsapp:+1415...)

Kullanim:
    from reymen.ag.whatsapp_gateway import whatsapp_gonder, motor_kaydet

    # Dogrudan kullanim
    sonuc = whatsapp_gonder(
        numara="+905551234567",
        mesaj="Merhaba Dunya!",
    )

Kosullar:
    pip install python-dotenv  (opsiyonel, .env yuklemek icin)
"""

from __future__ import annotations

import base64
import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Sabitler ────────────────────────────────────────────────────────────
ORTAM_SID = "WHATSAPP_ACCOUNT_SID"
ORTAM_TOKEN = "WHATSAPP_AUTH_TOKEN"
ORTAM_API_KEY = "WHATSAPP_API_KEY"
ORTAM_NUMARA = "WHATSAPP_NUMBER"
TWILIO_BASE = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
VARSAYILAN_TIMEOUT = 30


# ═══════════════════════════════════════════════════════════════════════
#  Yardimci: .env yukle
# ═══════════════════════════════════════════════════════════════════════


def _dotenv_yukle() -> None:
    """python-dotenv varsa .env dosyasini yukler."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def _ayar_al(anahtar: str, varsayilan: str = "") -> str:
    """Ortam degiskenini dondurur, .env'yi de dener."""
    return os.environ.get(anahtar, varsayilan).strip()


def _baglanti_bilgisi_al() -> dict[str, str]:
    """WhatsApp baglanti bilgilerini ortam degiskenlerinden alir."""
    _dotenv_yukle()

    # WHATSAPP_AUTH_TOKEN yoksa WHATSAPP_API_KEY'i dene
    token = _ayar_al(ORTAM_TOKEN) or _ayar_al(ORTAM_API_KEY)

    return {
        "account_sid": _ayar_al(ORTAM_SID),
        "auth_token": token,
        "from_number": _ayar_al(ORTAM_NUMARA),
    }


# ═══════════════════════════════════════════════════════════════════════
#  WhatsApp Mesaj Gonderme (Twilio REST API)
# ═══════════════════════════════════════════════════════════════════════


def whatsapp_gonder(
    numara: str,
    mesaj: str,
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
    from_number: Optional[str] = None,
) -> dict[str, Any]:
    """Twilio WhatsApp Business API ile mesaj gonderir.

    Args:
        numara: Alici telefon numarasi (+905551234567)
        mesaj: Gonderilecek mesaj metni
        account_sid: Twilio Account SID (bos = .env'den)
        auth_token: Twilio Auth Token (bos = .env'den)
        from_number: Twilio WhatsApp numarasi (bos = .env'den)

    Returns:
        {"basarili": True/False, "hata": "...", ...}
    """
    try:
        ayarlar = _baglanti_bilgisi_al()
        account_sid = account_sid or ayarlar["account_sid"]
        auth_token = auth_token or ayarlar["auth_token"]
        from_number = from_number or ayarlar["from_number"]

        # Gerekli alanlari kontrol et
        eksikler = []
        if not account_sid:
            eksikler.append(ORTAM_SID)
        if not auth_token:
            eksikler.append(f"{ORTAM_TOKEN} / {ORTAM_API_KEY}")
        if not from_number:
            eksikler.append(ORTAM_NUMARA)
        if not numara:
            eksikler.append("numara (parametre)")

        if eksikler:
            return {
                "basarili": False,
                "hata": f"Eksik ayarlar: {', '.join(eksikler)}",
            }

        # Twilio WhatsApp numara formatina cevir
        if not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"
        if not numara.startswith("whatsapp:"):
            alici = f"whatsapp:{numara}"
        else:
            alici = numara

        # HTTP POST istegi olustur
        url = TWILIO_BASE.format(sid=account_sid)
        veri = urllib.parse.urlencode({"From": from_number, "To": alici, "Body": mesaj}).encode(
            "utf-8"
        )

        # Basic Auth
        auth_b64 = base64.b64encode(
            f"{account_sid}:{auth_token}".encode("utf-8")
        ).decode("utf-8")

        istek = urllib.request.Request(
            url,
            data=veri,
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )

        with urllib.request.urlopen(istek, timeout=VARSAYILAN_TIMEOUT) as yanit:
            yanit_verisi = yanit.read().decode("utf-8")
            yanit_json = json.loads(yanit_verisi)

        logger.info(
            "[WhatsApp] Mesaj gonderildi -> %s (sid: %s)",
            numara,
            yanit_json.get("sid", "?"),
        )
        return {
            "basarili": True,
            "alici": numara,
            "twilio_sid": yanit_json.get("sid", ""),
            "durum": yanit_json.get("status", ""),
        }

    except urllib.error.HTTPError as e:
        hata_metni = ""
        try:
            hata_metni = e.read().decode("utf-8")
            hata_json = json.loads(hata_metni)
            hata_metni = hata_json.get("message", hata_metni)
        except Exception:
            hata_metni = str(e)
        hata = f"Twilio HTTP hatasi ({e.code}): {hata_metni}"
        logger.error("[WhatsApp] %s", hata)
        return {"basarili": False, "hata": hata}

    except urllib.error.URLError as e:
        hata = f"Baglanti hatasi: {e.reason}"
        logger.error("[WhatsApp] %s", hata)
        return {"basarili": False, "hata": hata}

    except Exception as e:
        hata = f"Beklenmeyen hata: {e}"
        logger.error("[WhatsApp] %s", hata)
        return {"basarili": False, "hata": hata}


# ═══════════════════════════════════════════════════════════════════════
#  Motor Kayit (plugin sistemi)
# ═══════════════════════════════════════════════════════════════════════


def motor_kaydet(motor: Any) -> None:
    """WhatsApp gonderici aracini motor sistemine kaydeder.

    Ornek kullanim:
        >>> motor_kaydet(motor)
        >>> # motor artik WHATSAPP_GONDER aracina sahip
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "WHATSAPP_GONDER",
        lambda numara="", mesaj="": whatsapp_gonder(numara, mesaj),
        "WhatsApp mesaji gonder (numara, mesaj)",
    )


# ═══════════════════════════════════════════════════════════════════════
#  Dogrudan calistirma (test)
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    import sys

    # Komut satirindan test: python whatsapp_gateway.py "+905551234567" "Mesaj"
    if len(sys.argv) >= 3:
        sonuc = whatsapp_gonder(numara=sys.argv[1], mesaj=sys.argv[2])
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    else:
        print("Kullanim: python whatsapp_gateway.py <telefon_numarasi> <mesaj>")
        print('Ornek:    python whatsapp_gateway.py "+905551234567" "Merhaba"')
