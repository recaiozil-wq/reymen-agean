# -*- coding: utf-8 -*-

__all__ = ['motor_kaydet']
import json
import os
import urllib.request


def _tg_gonder(metin: str, chat_id: str = "") -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not chat:
        return "[Telegram] TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID ayarli degil."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps({"chat_id": chat, "text": metin[:4000]}).encode()
    try:
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            sonuc = json.loads(r.read())
        return "[Telegram] Gonderildi." if sonuc.get("ok") else f"[Telegram] Hata: {sonuc}"
    except Exception as e:
        return f"[Telegram] Baglanti hatasi: {e}"


def motor_kaydet(motor):
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "TELEGRAM_BOT_GONDER",
        lambda metin="", chat_id="": _tg_gonder(metin, chat_id),
        "Telegram bot ile mesaj gonder (metin, chat_id: opsiyonel — bos=env'den)",
    )
