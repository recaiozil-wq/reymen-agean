# -*- coding: utf-8 -*-

"""
slack_gateway.py â€” Slack Mesaj Gonderme Gateway (Webhook).

Slack Incoming Webhook URL ile mesaj gonderir. Markdown destegi icerir.
Harici bir kutuphane GEREKTIRMEZ â€” urllib ile ham HTTP istegi gonderir.

Baglanti bilgileri .env dosyasindaki su degiskenlerden okunur:
  - SLACK_WEBHOOK_URL â€” Slack Incoming Webhook URL'si

Kullanim:
    from reymen.ag.slack_gateway import slack_gonder, motor_kaydet

    # Dogrudan kullanim
    sonuc = slack_gonder(
        mesaj="Merhaba Dunya!",
    )

    # Ozel webhook URL ile
    sonuc = slack_gonder(
        webhook_url="https://hooks.slack.com/services/...",
        mesaj="*KalÄ±n* ve ~ustu cizili~ metin",
    )

Kosullar:
    pip install python-dotenv  (opsiyonel, .env yuklemek icin)
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Optional

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ORTAM_WEBHOOK = "SLACK_WEBHOOK_URL"
VARSAYILAN_TIMEOUT = 30
VARSAYILAN_RENK = "#36a64f"  # Slack yesili


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  Slack Mesaj Gonderme (Incoming Webhook)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def slack_gonder(
    mesaj: str,
    webhook_url: Optional[str] = None,
    baslik: Optional[str] = None,
    renk: Optional[str] = None,
    kanal: Optional[str] = None,
    kullanici: Optional[str] = None,
    icon_emoji: Optional[str] = None,
) -> dict[str, Any]:
    """Slack Incoming Webhook ile mesaj gonderir.

    Markdown formatini destekler:
      - *kalÄ±n*    â†’ **bold**
      - _italik_   â†’ *italic*
      - ~ustu ciz~ â†’ ~~strikethrough~~
      - `kod`      â†’ inline code
      - ```blok``` â†’ code block
      - > alinti   â†’ blockquote

    Args:
        mesaj: Gonderilecek mesaj (Markdown/MRKDWN formatinda)
        webhook_url: Slack Webhook URL (bos = .env'den SLACK_WEBHOOK_URL)
        baslik: Isteg e bagli baslik (attachment basligi)
        renk: Sol cizgi rengi (varsayilan: yesil #36a64f)
        kanal: Hedef Slack kanali (ornek: #genel, @kullanici)
        kullanici: Bot gorunen adi
        icon_emoji: Bot emoji ikonu (ornek: :robot_face:)

    Returns:
        {"basarili": True/False, "hata": "...", ...}
    """
    try:
        url = webhook_url or _ayar_al(ORTAM_WEBHOOK)

        # Webhook URL'sini kontrol et
        if not url:
            return {
                "basarili": False,
                "hata": f"Eksik ayar: {ORTAM_WEBHOOK} â€” .env dosyanizi kontrol edin",
            }

        # Slack mesaj payload'i (mrkdwn ile)
        payload: dict[str, Any] = {
            "text": mesaj,
            "mrkdwn": True,  # Markdown destegi acik
        }

        # Opsiyonel alanlar
        if baslik:
            # Attachment (zengin mesaj) olarak gonder
            attachments = [
                {
                    "color": renk or VARSAYILAN_RENK,
                    "title": baslik,
                    "text": mesaj,
                    "mrkdwn_in": ["text", "title"],
                }
            ]
            payload["text"] = ""  # Ana metin bos
            payload["attachments"] = attachments

        if kanal:
            payload["channel"] = kanal
        if kullanici:
            payload["username"] = kullanici
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji

        # HTTP POST istegi
        veri = json.dumps(payload).encode("utf-8")
        istek = urllib.request.Request(
            url,
            data=veri,
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )

        with urllib.request.urlopen(istek, timeout=VARSAYILAN_TIMEOUT) as yanit:
            yanit_metni = yanit.read().decode("utf-8").strip()

        # Slack basarili yaniti: "ok" (duz metin)
        if yanit_metni == "ok":
            logger.info(
                "[Slack] Mesaj gonderildi -> %s",
                kanal or url.split("/")[-1][:16],
            )
            return {"basarili": True}

        logger.warning("[Slack] Beklenmeyen yanit: %s", yanit_metni)
        return {"basarili": False, "hata": f"Beklenmeyen yanit: {yanit_metni}"}

    except urllib.error.HTTPError as e:
        hata_metni = ""
        try:
            hata_metni = e.read().decode("utf-8")
        except Exception:
            hata_metni = str(e)
        hata = f"Slack HTTP hatasi ({e.code}): {hata_metni}"
        logger.error("[Slack] %s", hata)
        return {"basarili": False, "hata": hata}

    except urllib.error.URLError as e:
        hata = f"Baglanti hatasi: {e.reason}"
        logger.error("[Slack] %s", hata)
        return {"basarili": False, "hata": hata}

    except Exception as e:
        hata = f"Beklenmeyen hata: {e}"
        logger.error("[Slack] %s", hata)
        return {"basarili": False, "hata": hata}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  Motor Kayit (plugin sistemi)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def motor_kaydet(motor: Any) -> None:
    """Slack gonderici aracini motor sistemine kaydeder.

    Ornek kullanim:
        >>> motor_kaydet(motor)
        >>> # motor artik SLACK_GONDER aracina sahip
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "SLACK_GONDER",
        lambda mesaj="": slack_gonder(mesaj),
        "Slack kanalina mesaj gonder (mesaj, webhook_url: opsiyonel)",
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  Dogrudan calistirma (test)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    import sys

    # Komut satirindan test: python slack_gateway.py "Mesaj" [webhook_url]
    if len(sys.argv) >= 2:
        sonuc = slack_gonder(
            mesaj=sys.argv[1],
            webhook_url=sys.argv[2] if len(sys.argv) >= 3 else None,
        )
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    else:
        print("Kullanim: python slack_gateway.py <mesaj> [webhook_url]")
        print('Ornek:    python slack_gateway.py "*Merhaba* Dunya!"')
        print("          python slack_gateway.py 'Mesaj' https://hooks.slack.com/services/...")
