# -*- coding: utf-8 -*-
"""gateway/platforms/slack.py — Slack Platformu.

Webhook veya bot token ile Slack mesaji gonderir.
SlackAdapter — ReYMeN gateway plugin adaptörü.
"""

import logging
import os
import requests
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────
DEFAULT_MAX_TEXT_LENGTH = 4000


def check_slack_requirements() -> bool:
    """Slack adapter için gerekli bağımlılıkları kontrol et."""
    try:
        import slack_bolt  # noqa: F401
        return True
    except ImportError:
        return False


class SlackAdapter:
    """Slack platform adapter — gateway platformlari ile uyumlu.

    Attributes:
        config: Platform yapilandirma ayarlari.
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        self.config = config or {}
        self._token = os.environ.get("SLACK_BOT_TOKEN", "")
        self._webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")

    def send_message(self, hedef: str, mesaj: str, **kwargs) -> dict:
        """Slack kanalina mesaj gonder.

        Args:
            hedef: Webhook URL'si veya #kanal_adi
            mesaj: Gonderilecek metin
            **kwargs: Ek parametreler

        Returns:
            dict: Gonderim sonucu
        """
        if hedef.startswith("http"):
            return self._webhook_gonder(hedef, mesaj)
        return self._bot_gonder(hedef, mesaj)

    def _webhook_gonder(self, url: str, mesaj: str) -> dict:
        try:
            r = requests.post(url, json={"text": mesaj[:DEFAULT_MAX_TEXT_LENGTH]}, timeout=10)
            if r.status_code == 200:
                return {"status": "basarili", "message": "Mesaj gonderildi (webhook)."}
            return {"status": "hata", "error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"status": "hata", "error": str(e)}

    def _bot_gonder(self, kanal: str, mesaj: str) -> dict:
        if not self._token or self._token.startswith("***"):
            return {"status": "hata", "error": "SLACK_BOT_TOKEN ayarlanmamis."}
        try:
            r = requests.post(
                "https://slack.com/api/chat.postMessage",
                json={"channel": kanal, "text": mesaj[:DEFAULT_MAX_TEXT_LENGTH]},
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=10,
            )
            data = r.json()
            if data.get("ok"):
                return {"status": "basarili", "message_id": data.get("ts", "")}
            return {"status": "hata", "error": data.get("error", "bilinmiyor")}
        except Exception as e:
            return {"status": "hata", "error": str(e)}

    def ping(self) -> bool:
        """Slack API'ye erişilebilirliği kontrol et."""
        return bool(self._token or self._webhook_url)


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Slack kanalina mesaj gonder.

    Args:
        hedef: Webhook URL'si veya #kanal_adi
        mesaj: Gonderilecek metin
    """
    if hedef.startswith("http"):
        # Webhook
        try:
            r = requests.post(hedef, json={"text": mesaj[:4000]}, timeout=10)
            if r.status_code == 200:
                return "[Slack]: Mesaj gonderildi (webhook)."
            return f"[Slack]: Hata {r.status_code}"
        except Exception as e:
            return f"[Slack]: Hata: {e}"

    token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not token or token.startswith("***"):
        return "[Slack]: SLACK_BOT_TOKEN ayarlanmamis."

    try:
        r = requests.post(
            "https://slack.com/api/chat.postMessage",
            json={"channel": hedef, "text": mesaj[:4000]},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        data = r.json()
        if data.get("ok"):
            return "[Slack]: Mesaj gonderildi."
        return f"[Slack]: Hata: {data.get('error', 'bilinmiyor')}"
    except Exception as e:
        return f"[Slack]: Hata: {e}"



