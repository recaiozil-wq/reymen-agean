# -*- coding: utf-8 -*-
"""tools/discord_tool.py — Discord Aracı.

Discord Bot API v10 üzerinden mesaj gönderme, kanal okuma,
DM gönderme, webhook desteği.
ENV: DISCORD_BOT_TOKEN, DISCORD_DEFAULT_CHANNEL_ID
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Optional

DISCORD_TOKEN      = os.environ.get("DISCORD_BOT_TOKEN", "")
DISCORD_KANAL_ID   = os.environ.get("DISCORD_DEFAULT_CHANNEL_ID", "")
DISCORD_WEBHOOK    = os.environ.get("DISCORD_WEBHOOK_URL", "")
DISCORD_API        = "https://discord.com/api/v10"


def _discord_get(yol: str) -> dict | list:
    if not DISCORD_TOKEN:
        return {"error": "DISCORD_BOT_TOKEN ayarlanmamış."}
    try:
        req = urllib.request.Request(
            f"{DISCORD_API}{yol}",
            headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def _discord_post(yol: str, veri: dict) -> dict:
    if not DISCORD_TOKEN:
        return {"error": "DISCORD_BOT_TOKEN ayarlanmamış."}
    try:
        req = urllib.request.Request(
            f"{DISCORD_API}{yol}",
            data=json.dumps(veri).encode("utf-8"),
            headers={
                "Authorization": f"Bot {DISCORD_TOKEN}",
                "Content-Type":  "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


# ── Mesajlaşma ────────────────────────────────────────────────────────

def mesaj_gonder(mesaj: str, kanal_id: str = "", embed: Optional[dict] = None) -> str:
    """Kanala mesaj gönder.

    Args:
        mesaj:    Mesaj içeriği
        kanal_id: Kanal ID (boşsa DISCORD_DEFAULT_CHANNEL_ID)
        embed:    Discord embed dict (opsiyonel)

    Returns:
        Mesaj ID veya hata
    """
    hedef = kanal_id or DISCORD_KANAL_ID
    if not hedef:
        return "[Discord]: Kanal ID belirtilmedi. DISCORD_DEFAULT_CHANNEL_ID ayarla."

    veri: dict = {"content": mesaj}
    if embed:
        veri["embeds"] = [embed]

    yanit = _discord_post(f"/channels/{hedef}/messages", veri)
    if "error" in yanit:
        return f"[Discord]: {yanit['error']}"
    return f"Mesaj gönderildi: {yanit.get('id','')}"


def webhook_gonder(mesaj: str, kullanici_adi: str = "ReYMeN", embed: Optional[dict] = None) -> str:
    """Webhook üzerinden mesaj gönder (Token gerektirmez).

    Args:
        mesaj:       Mesaj içeriği
        kullanici_adi: Bot görünen adı
        embed:       Discord embed (opsiyonel)
    """
    if not DISCORD_WEBHOOK:
        return "[Discord Webhook]: DISCORD_WEBHOOK_URL ayarlanmamış."

    veri: dict = {"content": mesaj, "username": kullanici_adi}
    if embed:
        veri["embeds"] = [embed]

    try:
        req = urllib.request.Request(
            DISCORD_WEBHOOK,
            data=json.dumps(veri).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return "Webhook mesajı gönderildi." if r.status < 300 else f"HTTP {r.status}"
    except Exception as e:
        return f"[Discord Webhook]: {e}"


def dm_gonder(kullanici_id: str, mesaj: str) -> str:
    """Kullanıcıya DM gönder.

    Args:
        kullanici_id: Discord kullanıcı ID'si
        mesaj:        Mesaj içeriği
    """
    dm_kanal = _discord_post("/users/@me/channels", {"recipient_id": kullanici_id})
    if "error" in dm_kanal:
        return f"[Discord DM]: DM kanalı açılamadı — {dm_kanal['error']}"

    kanal_id = dm_kanal.get("id", "")
    return mesaj_gonder(mesaj, kanal_id)


# ── Okuma ─────────────────────────────────────────────────────────────

def kanal_mesajlari(kanal_id: str = "", limit: int = 10) -> str:
    """Kanal mesajlarını oku.

    Args:
        kanal_id: Kanal ID (boşsa varsayılan)
        limit:    Kaç mesaj (max 100)

    Returns:
        Mesajlar metin olarak
    """
    hedef = kanal_id or DISCORD_KANAL_ID
    if not hedef:
        return "[Discord]: Kanal ID belirtilmedi."

    yanit = _discord_get(f"/channels/{hedef}/messages?limit={min(limit, 100)}")
    if isinstance(yanit, dict) and "error" in yanit:
        return f"[Discord]: {yanit['error']}"

    mesajlar = yanit if isinstance(yanit, list) else []
    if not mesajlar:
        return "Mesaj yok."

    satirlar = [f"Discord Mesajları ({len(mesajlar)}):"]
    for m in mesajlar:
        yazar = m.get("author", {})
        satirlar.append(
            f"\n[{m.get('timestamp','')[:19]}] "
            f"{yazar.get('global_name') or yazar.get('username','?')}: "
            f"{m.get('content','')}"
        )
    return "\n".join(satirlar)


def sunucu_listesi() -> str:
    """Botun bulunduğu sunucuları listele."""
    yanit = _discord_get("/users/@me/guilds")
    if isinstance(yanit, dict) and "error" in yanit:
        return f"[Discord]: {yanit['error']}"

    sunucular = yanit if isinstance(yanit, list) else []
    if not sunucular:
        return "Bot hiçbir sunucuda değil."

    satirlar = [f"Discord Sunucuları ({len(sunucular)}):"]
    for s in sunucular:
        satirlar.append(f"  [{s.get('id')}] {s.get('name')}")
    return "\n".join(satirlar)


def embed_olustur(baslik: str, aciklama: str, renk: int = 0x5865F2) -> dict:
    """Discord embed oluştur."""
    return {"title": baslik, "description": aciklama, "color": renk}


def motor_kaydet(motor):
    """Discord araçlarını motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "DISCORD_MESAJ_GONDER",
        lambda mesaj, kanal_id="": mesaj_gonder(mesaj, kanal_id),
        "Discord kanalına mesaj gönder",
    )
    motor._plugin_arac_kaydet(
        "DISCORD_WEBHOOK",
        lambda mesaj, kullanici_adi="ReYMeN": webhook_gonder(mesaj, kullanici_adi),
        "Discord webhook üzerinden mesaj gönder",
    )
    motor._plugin_arac_kaydet(
        "DISCORD_DM",
        lambda kullanici_id, mesaj: dm_gonder(kullanici_id, mesaj),
        "Discord kullanıcısına DM gönder",
    )
    motor._plugin_arac_kaydet(
        "DISCORD_OKU",
        lambda kanal_id="", limit=10: kanal_mesajlari(kanal_id, int(limit)),
        "Discord kanal mesajlarını oku",
    )
    motor._plugin_arac_kaydet(
        "DISCORD_SUNUCULAR",
        lambda: sunucu_listesi(),
        "Botun bulunduğu Discord sunucularını listele",
    )


def run(action: str = "mesaj_gonder", mesaj: str = "", kanal_id: str = "", kullanici_id: str = "", embed: dict | None = None, limit: int = 10) -> str:
    """Discord aracının genel run() wrapper'ı."""
    if action == "mesaj_gonder":
        return mesaj_gonder(mesaj, kanal_id)
    if action == "webhook_gonder":
        return webhook_gonder(mesaj, kanal_id or "ReYMeN")
    if action == "dm_gonder":
        return dm_gonder(kullanici_id, mesaj)
    if action == "kanal_mesajlari":
        return kanal_mesajlari(kanal_id, limit)
    if action == "sunucu_listesi":
        return sunucu_listesi()
    return f"[Discord]: Bilinmeyen action: {action}. Desteklenen: mesaj_gonder, webhook_gonder, dm_gonder, kanal_mesajlari, sunucu_listesi"


if __name__ == "__main__":
    print(f"Token: {'✓' if DISCORD_TOKEN else '✗'}")
    if DISCORD_TOKEN:
        print(sunucu_listesi())
