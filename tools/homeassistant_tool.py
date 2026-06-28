# -*- coding: utf-8 -*-
"""homeassistant_tool.py — Home Assistant Entegrasyonu.

Home Assistant REST API uzerinden entity okuma ve servis cagirma.
ENV: HA_TOKEN
"""

import json
import os
import urllib.request

HA_TOKEN = os.environ.get("HA_TOKEN", "")
HA_API_BASE = "http://homeassistant.local:8123/api/"


def _ha_get(yol: str) -> dict | list:
    """Home Assistant API'ye GET istegi yap."""
    if not HA_TOKEN:
        return {"error": "HA_TOKEN ayarlanmamis."}
    try:
        req = urllib.request.Request(
            f"{HA_API_BASE}{yol}",
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return {"error": "Home Assistant baglantisi kurulamadi"}


def _ha_post(yol: str, veri: dict) -> dict:
    """Home Assistant API'ye POST istegi yap."""
    if not HA_TOKEN:
        return {"error": "HA_TOKEN ayarlanmamis."}
    try:
        req = urllib.request.Request(
            f"{HA_API_BASE}{yol}",
            data=json.dumps(veri).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return {"error": "Home Assistant baglantisi kurulamadi"}


def run(**kwargs) -> str:
    """Home Assistant islemlerini yapar.

    Args:
        islem (zorunlu): "entity_oku", "servis_cagir", "durum"
        entity_id: Entity ID (ornek: light.oturma_odasi)
        servis: Cagrilacak servis (ornek: light.turn_on)
        alan_adi: Servis alan adi (ornek: brightness)
        deger: Servis degeri (ornek: 255)

    Returns:
        Islem sonucu metin olarak
    """
    try:
        islem = kwargs.get("islem")
        if not islem:
            return "Hata: 'islem' parametresi zorunludur (entity_oku, servis_cagir, durum)."

        if islem == "entity_oku":
            entity_id = kwargs.get("entity_id")
            if not entity_id:
                return "Hata: 'entity_id' parametresi zorunludur."
            return _entity_oku(entity_id)

        elif islem == "servis_cagir":
            servis = kwargs.get("servis")
            if not servis:
                return "Hata: 'servis' parametresi zorunludur (ornek: light.turn_on)."

            alan_adi = kwargs.get("alan_adi", "")
            deger = kwargs.get("deger", "")
            entity_id = kwargs.get("entity_id", "")

            return _servis_cagir(servis, entity_id, alan_adi, deger)

        elif islem == "durum":
            return _genel_durum()

        else:
            return f"Hata: Gecersiz islem '{islem}'. Secenekler: entity_oku, servis_cagir, durum."

    except Exception as e:
        return f"Hata: {e}"


def _entity_oku(entity_id: str) -> str:
    """Entity durumunu oku."""
    yanit = _ha_get(f"states/{entity_id}")
    if isinstance(yanit, dict) and "error" in yanit:
        return yanit["error"]

    if isinstance(yanit, dict):
        state = yanit.get("state", "bilinmiyor")
        attr = yanit.get("attributes", {})
        satirlar = [f"[Home Assistant] {entity_id}: {state}"]
        for k, v in attr.items():
            if k in ("friendly_name", "brightness", "temperature", "humidity",
                      "current_temperature", "color_temp", "rgb_color"):
                satirlar.append(f"  {k}: {v}")
        return "\n".join(satirlar)

    return json.dumps(yanit, indent=2, ensure_ascii=False)


def _servis_cagir(servis: str, entity_id: str, alan_adi: str, deger: str) -> str:
    """Servis cagir."""
    domain, service = servis.split(".", 1) if "." in servis else (servis, "")

    veri = {}
    if entity_id:
        veri["entity_id"] = [entity_id]
    if alan_adi and deger:
        # Deger donusumu
        try:
            if "." in deger:
                veri[alan_adi] = float(deger)
            else:
                veri[alan_adi] = int(deger)
        except ValueError:
            veri[alan_adi] = deger

    yanit = _ha_post(f"services/{domain}/{service}", veri)
    if isinstance(yanit, dict) and "error" in yanit:
        return yanit["error"]

    return f"Servis cagrildi: {servis} -> {'basarili' if yanit else 'yanit alinamadi'}"


def _genel_durum() -> str:
    """Home Assistant genel durum bilgisi."""
    yanit = _ha_get("")
    if isinstance(yanit, dict) and "error" in yanit:
        return yanit["error"]

    durum = ""
    if isinstance(yanit, dict):
        durum = yanit.get("message", yanit.get("state", "baglandi"))

    # Entity sayisi
    states = _ha_get("states")
    entity_sayisi = len(states) if isinstance(states, list) else 0

    return (
        f"[Home Assistant Durum]\n"
        f"  Baglanti: {durum}\n"
        f"  Entity sayisi: {entity_sayisi}\n"
        f"  API: {HA_API_BASE}"
    )


if __name__ == "__main__":
    print(f"HA_TOKEN: {'✓' if HA_TOKEN else '✗'}")
    print(run(islem="durum"))
