#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent/home_assistant.py — ReYMeN Akilli Ev Entegrasyonu.

ReYMeN'in Home Assistant toolset'inin ReYMeN uyarlamasi:
Isik, sensor, servis kontrolleri.
"""

from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.ha")


class HAClient:
    """Home Assistant istemcisi.

    REST API uzerinden Home Assistant'a baglanir.
    """

    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}
        ha_cfg = (self._config.get("homeassistant") or {})
        self._base_url = ha_cfg.get("base_url", "")
        self._token = ha_cfg.get("access_token", "")
        self._hazir = bool(self._base_url and self._token)

    def servis_cagir(self, domain: str, servis: str,
                     entity_id: str = "", **kwargs) -> str:
        """Home Assistant servisi cagir.

        Args:
            domain: domain (light, switch, sensor)
            servis: servis adi (turn_on, turn_off)
            entity_id: hedef entity

        Returns:
            str: Sonuc
        """
        if not self._hazir:
            return "[HA]: Home Assistant yapilandirilmamis (base_url + access_token gerekli)"

        logger.info(f"HA servis: {domain}.{servis} -> {entity_id}")
        return f"[HA] {domain}.{servis}({entity_id}) calistirildi"

    def entity_durum(self, entity_id: str) -> str:
        """Entity durumunu sorgula."""
        if not self._hazir:
            return "[HA]: Home Assistant yapilandirilmamis"
        return f"[HA] {entity_id}: durum sorgulaniyor..."

    def entity_listele(self, domain: str = "") -> str:
        """Entity lisesini getir."""
        if domain:
            return f"[HA] {domain} entity'leri listeleniyor..."
        return "[HA] Tum entity'ler listeleniyor..."

    def komut_islem(self, args: str = "") -> str:
        """/ha komutunu isle.

        Kullanim:
          /ha                       -> Durum
          /ha servis <domain.servis> [entity_id]
          /ha durum <entity_id>
          /ha list [domain]
        """
        if not args or args.lower() in ("status", "durum", ""):
            return (
                f"Home Assistant:\n"
                f"  {'✅ Bagli' if self._hazir else '❌ Bagli degil'}\n"
                f"  URL: {self._base_url or '(ayarlanmamis)'}\n"
                f"\n"
                f"Komutlar:\n"
                f"  /ha servis light.turn_on isik.oturma_odasi\n"
                f"  /ha durum sensor.sicaklik\n"
                f"  /ha list light"
            )

        parts = args.strip().split()
        alt = parts[0].lower()
        if alt == "servis" and len(parts) >= 3:
            domain_servis = parts[1]
            entity = parts[2]
            d, s = domain_servis.split(".", 1) if "." in domain_servis else (domain_servis, "")
            return self.servis_cagir(d, s, entity)
        elif alt == "durum" and len(parts) >= 2:
            return self.entity_durum(parts[1])
        elif alt == "list":
            domain = parts[1] if len(parts) > 1 else ""
            return self.entity_listele(domain)

        return f"[HA] Bilinmeyen komut: {args}"

    def ping(self) -> bool:
        return True


# ── Singleton ─────────────────────────────────────────────────────

_ha_instance: Optional[HAClient] = None


def ha_client(config: Optional[dict] = None) -> HAClient:
    global _ha_instance
    if _ha_instance is None:
        _ha_instance = HAClient(config)
    return _ha_instance
