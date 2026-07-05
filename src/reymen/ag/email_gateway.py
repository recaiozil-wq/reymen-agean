# -*- coding: utf-8 -*-
"""
email_gateway.py â€” E-posta Gonderme Gateway.

smtplib (SMTP_SSL) kullanarak e-posta gonderir.
Baglanti bilgileri .env dosyasindaki su degiskenlerden okunur:
  - EMAIL_HOST (orn. smtp.gmail.com)
  - EMAIL_PORT (orn. 465)
  - EMAIL_USER (e-posta adresi)
  - EMAIL_PASS (uygulama sifresi / token)

Kullanim:
    from reymen.ag.email_gateway import email_gonder, motor_kaydet

    # Dogrudan kullanim
    sonuc = email_gonder(
        konu="Test",
        icerik="Merhaba Dunya!",
        alici="ornek@email.com",
    )

Kosullar:
    pip install python-dotenv
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ORTAM_HOST = "EMAIL_HOST"
ORTAM_PORT = "EMAIL_PORT"
ORTAM_USER = "EMAIL_USER"
ORTAM_PASS = "EMAIL_PASS"
VARSAYILAN_PORT = 465
VARSAYILAN_TIMEOUT = 30


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  Yardimci: .env yukle
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


def _baglanti_bilgisi_al() -> dict[str, Any]:
    """E-posta SMTP baglanti bilgilerini ortam degiskenlerinden alir."""
    _dotenv_yukle()
    port_raw = _ayar_al(ORTAM_PORT)
    try:
        port = int(port_raw) if port_raw else VARSAYILAN_PORT
    except (ValueError, TypeError):
        port = VARSAYILAN_PORT

    return {
        "host": _ayar_al(ORTAM_HOST),
        "port": port,
        "user": _ayar_al(ORTAM_USER),
        "password": _ayar_al(ORTAM_PASS),
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  E-posta Gonderme
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def email_gonder(
    konu: str,
    icerik: str,
    alici: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    kullanici: Optional[str] = None,
    sifre: Optional[str] = None,
    html: bool = False,
) -> dict[str, Any]:
    """SMTP_SSL ile e-posta gonderir.

    Args:
        konu: E-posta konusu
        icerik: E-posta icerigi (duz metin veya HTML)
        alici: Alici e-posta adresi
        host: SMTP sunucu adresi (bos = .env'den)
        port: SMTP portu (bos = .env'den veya 465)
        kullanici: SMTP kullanici adi (bos = .env'den)
        sifre: SMTP sifresi (bos = .env'den)
        html: True ise icerik HTML olarak gonderilir

    Returns:
        {"basarili": True/False, "hata": "...", ...}
    """
    try:
        # Baglanti bilgilerini al
        ayarlar = _baglanti_bilgisi_al()
        host = host or ayarlar["host"]
        port = port or ayarlar["port"]
        kullanici = kullanici or ayarlar["user"]
        sifre = sifre or ayarlar["password"]

        # Gerekli alanlari kontrol et
        eksikler = []
        if not host:
            eksikler.append(ORTAM_HOST)
        if not kullanici:
            eksikler.append(ORTAM_USER)
        if not sifre:
            eksikler.append(ORTAM_PASS)
        if not alici:
            eksikler.append("alici (parametre)")

        if eksikler:
            return {
                "basarili": False,
                "hata": f"Eksik ayarlar: {', '.join(eksikler)}",
            }

        # Tip daraltma â€” bu noktada hepsi dolu (type checker icin)
        assert host is not None and port is not None
        assert kullanici is not None and sifre is not None
        assert alici is not None

        # E-posta mesajini olustur
        mesaj = MIMEMultipart("alternative")
        mesaj["Subject"] = konu
        mesaj["From"] = kullanici
        mesaj["To"] = alici

        # Icerik ekle (duz metin + istege bagli HTML)
        mesaj.attach(MIMEText(icerik, "html" if html else "plain", "utf-8"))

        # SMTP_SSL ile gonder
        with smtplib.SMTP_SSL(
            host=host, port=port, timeout=VARSAYILAN_TIMEOUT
        ) as sunucu:
            sunucu.login(kullanici, sifre)
            sunucu.sendmail(kullanici, [alici], mesaj.as_string())

        logger.info("[Email] Mesaj gonderildi -> %s (konu: %s)", alici, konu)
        return {
            "basarili": True,
            "alici": alici,
            "konu": konu,
        }

    except smtplib.SMTPAuthenticationError:
        hata = "SMTP kimlik dogrulama hatasi â€” kullanici/sifre yanlis"
        logger.error("[Email] %s", hata)
        return {"basarili": False, "hata": hata}

    except smtplib.SMTPException as e:
        hata = f"SMTP hatasi: {e}"
        logger.error("[Email] %s", hata)
        return {"basarili": False, "hata": hata}

    except Exception as e:
        hata = f"Beklenmeyen hata: {e}"
        logger.error("[Email] %s", hata)
        return {"basarili": False, "hata": hata}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  Motor Kayit (plugin sistemi)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def motor_kaydet(motor: Any) -> None:
    """E-posta gonderici aracini motor sistemine kaydeder.

    Ornek kullanim:
        >>> motor_kaydet(motor)
        >>> # motor artik EMAIL_GONDER aracina sahip
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "EMAIL_GONDER",
        lambda konu="", icerik="", alici="": email_gonder(konu, icerik, alici),
        "E-posta gonder (konu, icerik, alici)",
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  Dogrudan calistirma (test)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    import json
    import sys

    # Komut satirindan test: python email_gateway.py "konu" "icerik" "alici"
    if len(sys.argv) >= 4:
        sonuc = email_gonder(
            konu=sys.argv[1],
            icerik=sys.argv[2],
            alici=sys.argv[3],
        )
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    else:
        print("Kullanim: python email_gateway.py <konu> <icerik> <alici>")
        print("Ornek:    python email_gateway.py Test \"Merhaba\" test@example.com")
