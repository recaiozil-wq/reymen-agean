# -*- coding: utf-8 -*-
"""tools/slack_tool.py — Slack Mesajlasma Araci.

Slack webhook veya bot token ile mesaj gonderir.
ENV: SLACK_BOT_TOKEN, SLACK_WEBHOOK_URL, SLACK_DEFAULT_CHANNEL
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Optional

SLACK_TOKEN   = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL", "")
SLACK_KANAL   = os.environ.get("SLACK_DEFAULT_CHANNEL", "#genel")
SLACK_API     = "https://slack.com/api"


def _slack_post(yol: str, veri: dict) -> dict:
    """Slack API'ye POST istegi gonder (bot token ile).

    Args:
        yol: API yolu (ornek: /chat.postMessage)
        veri: Gonderilecek JSON verisi

    Returns:
        dict: Slack API yaniti
    """
    if not SLACK_TOKEN:
        return {"error": "SLACK_BOT_TOKEN ayarlanmamis."}
    try:
        payload = json.dumps(veri).encode("utf-8")
        req = urllib.request.Request(
            f"{SLACK_API}{yol}",
            data=payload,
            headers={
                "Authorization": f"Bearer {SLACK_TOKEN}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def _webhook_gonder(url: str, veri: dict) -> dict:
    """Slack webhook'una POST istegi gonder.

    Args:
        url: Webhook URL'si
        veri: Gonderilecek JSON verisi

    Returns:
        dict: {"ok": True} veya {"error": ...}
    """
    try:
        payload = json.dumps(veri).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status == 200:
                return {"ok": True}
            return {"error": f"HTTP {r.status}: {r.read().decode('utf-8')[:200]}"}
    except Exception as e:
        return {"error": str(e)}


# ── Mesajlasma ────────────────────────────────────────────────────────

def mesaj_gonder(mesaj: str, kanal: str = "", thread_ts: str = "") -> str:
    """Slack kanalina mesaj gonder.

    Args:
        mesaj:    Gonderilecek metin (max 4000 karakter)
        kanal:   Slack kanal adi (#genel) veya ID'si (bos = SLACK_DEFAULT_CHANNEL)
        thread_ts: Bir thread'e yanit olarak gonderilecek timestamp

    Returns:
        Durum mesaji
    """
    # once webhook dene
    webhook_url = kanal if kanal.startswith("http") else SLACK_WEBHOOK
    if webhook_url:
        veri = {"text": mesaj[:4000]}
        if thread_ts:
            veri["thread_ts"] = thread_ts
        yanit = _webhook_gonder(webhook_url, veri)
        if yanit.get("ok"):
            return "[Slack]: Mesaj gonderildi (webhook)."
        return f"[Slack]: Webhook hatasi: {yanit.get('error', 'bilinmiyor')}"

    hedef = kanal or SLACK_KANAL
    if not hedef:
        return "[Slack]: Kanal belirtilmedi. SLACK_DEFAULT_CHANNEL ayarla veya kanal parametresi ver."

    veri = {
        "channel": hedef,
        "text": mesaj[:4000],
    }
    if thread_ts:
        veri["thread_ts"] = thread_ts

    yanit = _slack_post("/chat.postMessage", veri)
    if "error" in yanit:
        return f"[Slack]: {yanit['error']}"
    if yanit.get("ok"):
        return f"[Slack]: Mesaj gonderildi (ts: {yanit.get('ts', '?')})."
    return f"[Slack]: Hata: {yanit.get('error', 'bilinmiyor')}"


def kanal_mesajlari_getir(kanal: str, limit: int = 10) -> list:
    """Bir Slack kanalindaki son mesajlari getir.

    Args:
        kanal: Kanal ID'si
        limit: Kac mesaj (max 100)

    Returns:
        list: Mesaj listesi
    """
    yanit = _slack_post("/conversations.history", {
        "channel": kanal,
        "limit": min(limit, 100),
    })
    if "error" in yanit:
        return [{"error": yanit["error"]}]
    return yanit.get("messages", [])


def kullanici_bul(isim: str) -> Optional[str]:
    """Slack kullanicisini isme gore ara.

    Args:
        isim: Kullanici adi veya gorunen ad

    Returns:
        Kullanici ID'si veya None
    """
    yanit = _slack_post("/users.list", {})
    if "error" in yanit:
        return None
    for u in yanit.get("members", []):
        prof = u.get("profile", {})
        if isim.lower() in (u.get("name", "").lower(), prof.get("display_name", "").lower(), prof.get("real_name", "").lower()):
            return u.get("id")
    return None


def ping() -> str:
    """Slack API baglantisini test et.

    Returns:
        Durum mesaji
    """
    if SLACK_TOKEN:
        yanit = _slack_post("/auth.test", {})
        if "error" in yanit:
            return f"[Slack]: Baglanti hatasi: {yanit['error']}"
        if yanit.get("ok"):
            takim = yanit.get("team", "?")
            kullanici = yanit.get("user", "?")
            return f"[Slack]: Baglanti basarili. Takim: {takim}, Kullanici: {kullanici}"
        return f"[Slack]: Baglanti hatasi: {yanit}"
    if SLACK_WEBHOOK:
        return "[Slack]: Webhook yapilandirilmis (test icin mesaj gonderin)."
    return "[Slack]: SLACK_BOT_TOKEN veya SLACK_WEBHOOK_URL ayarlanmamis."


def run(param: str = "") -> str:
    """ToolRegistry icin giris noktasi.

    Kullanim:
        SLACK_MESAJ_GONDER("merhaba dunya")
        SLACK_MESAJ_GONDER("merhaba #kanal")
        SLACK_MESAJ_GONDER("merhaba #kanal thread_ts=123.456")

    Args:
        param: Mesaj icerigi veya "mesaj #kanal" formati

    Returns:
        Islem sonucu
    """
    if not param or param.strip() in ("", "ping", "test"):
        return ping()

    thread_ts = ""
    kanal = ""

    # Parametre: "mesaj #kanal" veya "mesaj"
    # thread_ts icin "mesaj thread_ts=XXX"
    parts = param.split()
    if len(parts) >= 2:
        for p in parts:
            if p.startswith("#"):
                kanal = p
            elif p.startswith("thread_ts="):
                thread_ts = p.split("=", 1)[1]

    if kanal:
        # kanal var, thread_ts anahtarini mesajdan cikar
        mesaj_parcalari = [p for p in parts if not p.startswith("#") and not p.startswith("thread_ts=")]
    else:
        mesaj_parcalari = [p for p in parts if not p.startswith("thread_ts=")]

    mesaj = " ".join(mesaj_parcalari)
    if not mesaj:
        return ping()

    return mesaj_gonder(mesaj, kanal=kanal, thread_ts=thread_ts)


if __name__ == "__main__":
    print("Slack Tool Test")
    print(f"  Token: {'***' if SLACK_TOKEN else 'ayarlanmamis'}")
    print(f"  Webhook: {'***' if SLACK_WEBHOOK else 'ayarlanmamis'}")
    print(f"  Kanal: {SLACK_KANAL}")
    print(f"  ping: {ping()}")
    print(f"  run('test'): {run('test')}")
