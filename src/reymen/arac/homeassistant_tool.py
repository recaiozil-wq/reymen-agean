# -*- coding: utf-8 -*-
"""homeassistant_tool.py â€” Home Assistant AkÄ±llÄ± Ev AracÄ±.

Home Assistant REST API Ã¼zerinden entitiy sorgulama, servis Ã§aÄŸÄ±rma
ve otomasyon tetikleme. gateway/homeassistant.py'den baÄŸÄ±msÄ±z, doÄŸrudan motor aracÄ±.
ENV: HA_URL, HA_TOKEN
"""

import json
import os
import urllib.request
from typing import Optional

HA_URL = os.environ.get("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.environ.get("HA_TOKEN", "")


def _ha_get(yol: str) -> dict | list:
    if not HA_TOKEN:
        return {"error": "HA_TOKEN ayarlanmamÄ±ÅŸ."}
    try:
        req = urllib.request.Request(
            f"{HA_URL.rstrip('/')}{yol}",
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def _ha_post(yol: str, veri: dict) -> dict:
    if not HA_TOKEN:
        return {"error": "HA_TOKEN ayarlanmamÄ±ÅŸ."}
    try:
        req = urllib.request.Request(
            f"{HA_URL.rstrip('/')}{yol}",
            data=json.dumps(veri).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def durum_oku(entity_id: str) -> str:
    """Bir entity'nin durumunu oku.

    Args:
        entity_id: HA entity ID'si (Ã¶r. light.salon, sensor.sicaklik)

    Returns:
        Durum ve Ã¶zellikler metin olarak
    """
    yanit = _ha_get(f"/api/states/{entity_id}")
    if isinstance(yanit, dict) and "error" in yanit:
        return f"[HA]: {yanit['error']}"
    if isinstance(yanit, dict):
        durum = yanit.get("state", "bilinmiyor")
        nit = yanit.get("attributes", {})
        return f"{entity_id}: {durum} | {json.dumps(nit, ensure_ascii=False)}"
    return str(yanit)


def tum_durumlar(domain: str = "") -> str:
    """TÃ¼m entity durumlarÄ±nÄ± listele.

    Args:
        domain: Filtre (Ã¶r. light, switch, sensor) â€” boÅŸsa hepsi

    Returns:
        Entity listesi metin olarak
    """
    yanit = _ha_get("/api/states")
    if isinstance(yanit, dict) and "error" in yanit:
        return f"[HA]: {yanit['error']}"

    entitiler = yanit if isinstance(yanit, list) else []
    if domain:
        entitiler = [
            e for e in entitiler if e.get("entity_id", "").startswith(domain + ".")
        ]

    if not entitiler:
        return (
            f"Domain '{domain}' iÃ§in entity bulunamadÄ±."
            if domain
            else "HiÃ§ entity yok."
        )

    satirlar = [f"Home Assistant Entity'leri ({len(entitiler)}):"]
    for e in entitiler[:50]:
        satirlar.append(f"  {e.get('entity_id')}: {e.get('state')}")
    if len(entitiler) > 50:
        satirlar.append(f"  ... ve {len(entitiler)-50} daha")
    return "\n".join(satirlar)


def servis_cagir(domain: str, servis: str, entity_id: str = "", **kwargs) -> str:
    """Home Assistant servisi Ã§aÄŸÄ±r.

    Args:
        domain:    Servis domain'i (Ã¶r. light, switch, script)
        servis:    Servis adÄ± (Ã¶r. turn_on, turn_off, toggle)
        entity_id: Hedef entity (boÅŸsa tÃ¼m domain)

    Returns:
        SonuÃ§ metni
    """
    veri: dict = {}
    if entity_id:
        veri["entity_id"] = entity_id
    veri.update(kwargs)

    yanit = _ha_post(f"/api/services/{domain}/{servis}", veri)
    if isinstance(yanit, dict) and "error" in yanit:
        return f"[HA Servis]: {yanit['error']}"
    return f"OK: {domain}.{servis} Ã§aÄŸrÄ±ldÄ±."


def isik_ac(entity_id: str, parlaklik: Optional[int] = None) -> str:
    """IÅŸÄ±k aÃ§."""
    kw = {"brightness": parlaklik} if parlaklik is not None else {}
    return servis_cagir("light", "turn_on", entity_id, **kw)


def isik_kapat(entity_id: str) -> str:
    """IÅŸÄ±k kapat."""
    return servis_cagir("light", "turn_off", entity_id)


def switch_toglle(entity_id: str) -> str:
    """Switch'i aÃ§/kapat."""
    return servis_cagir("switch", "toggle", entity_id)


def otomasyon_calistir(otomasyon_id: str) -> str:
    """Otomasyon tetikle."""
    return servis_cagir("automation", "trigger", otomasyon_id)


def motor_kaydet(motor):
    """HA araÃ§larÄ±nÄ± motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "HA_DURUM",
        lambda entity_id: durum_oku(entity_id),
        "Home Assistant entity durumunu oku",
    )
    motor._plugin_arac_kaydet(
        "HA_TUM_DURUMLAR",
        lambda domain="": tum_durumlar(domain),
        "TÃ¼m HA entity'lerini listele",
    )
    motor._plugin_arac_kaydet(
        "HA_SERVIS",
        lambda domain, servis, entity_id="": servis_cagir(domain, servis, entity_id),
        "Home Assistant servisi Ã§aÄŸÄ±r",
    )
    motor._plugin_arac_kaydet(
        "HA_ISIK_AC",
        lambda entity_id, parlaklik="": isik_ac(
            entity_id, int(parlaklik) if parlaklik else None
        ),
        "IÅŸÄ±k aÃ§",
    )
    motor._plugin_arac_kaydet(
        "HA_ISIK_KAPAT",
        lambda entity_id: isik_kapat(entity_id),
        "IÅŸÄ±k kapat",
    )
    motor._plugin_arac_kaydet(
        "HA_SWITCH",
        lambda entity_id: switch_toglle(entity_id),
        "Switch'i aÃ§/kapat",
    )
    motor._plugin_arac_kaydet(
        "HA_OTOMASYON",
        lambda otomasyon_id: otomasyon_calistir(otomasyon_id),
        "HA otomasyonunu tetikle",
    )


if __name__ == "__main__":
    print(f"HA URL: {HA_URL}")
    print(f"Token: {'âœ“' if HA_TOKEN else 'âœ—'}")
    if HA_TOKEN:
        print(tum_durumlar("light"))
