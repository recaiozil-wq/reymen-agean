#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent/toolset_manager.py — ReYMeN Toolset Yöneticisi.

Toolset'ler: arac gruplarini kategorilere ayirir,
ilgili araclari toplu acma/kapama, config entegrasyonu.
"""

from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.toolset")


# Varsayilan toolset tanimlari
DEFAULT_TOOLSETS = {
    "terminal": {
        "aciklama": "Shell komutlari, terminal islemleri",
        "araclar": ["terminal", "bash", "shell", "subprocess"],
    },
    "file": {
        "aciklama": "Dosya okuma/yazma, arama",
        "araclar": ["read_file", "write_file", "search_files", "patch"],
    },
    "web": {
        "aciklama": "Web arama, sayfa okuma",
        "araclar": ["web_search", "web_extract", "browser"],
    },
    "communication": {
        "aciklama": "Kullanici iletisimi",
        "araclar": ["clarify", "send_message", "notify"],
    },
    "coding": {
        "aciklama": "Kod yazma, calistirma, debug",
        "araclar": ["execute_code", "terminal", "patch"],
    },
    "data": {
        "aciklama": "Veri analizi, SQL, pandas",
        "araclar": ["execute_code", "sql", "query"],
    },
    "delegation": {
        "aciklama": "Alt ajan yonetimi",
        "araclar": ["delegate_task", "subagent"],
    },
    "memory": {
        "aciklama": "Hafiza ve ogrenme",
        "araclar": ["memory", "skill_view", "skill_manage"],
    },
    "automation": {
        "aciklama": "Otomasyon ve zamanlanmis gorevler",
        "araclar": ["cron", "schedule", "webhook"],
    },
}


class ToolsetManager:
    """Arac gruplarini yonetir.

    Her toolset bir kategoriyi temsil eder.
    Config'den hangi toolset'lerin aktif oldugu belirlenir.
    """

    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}
        ts_cfg = (self._config.get("toolsets") or {})

        # Tanimli toolset'ler (varsayilan + config'den ozel)
        self._toolsets = dict(DEFAULT_TOOLSETS)
        ozel = ts_cfg.get("custom", {})
        if isinstance(ozel, dict):
            self._toolsets.update(ozel)

        # Aktif toolset'ler (varsayilan: tumu)
        self._aktif = set(
            ts_cfg.get("enabled", list(self._toolsets.keys()))
        )

        logger.info(f"ToolsetManager: {len(self._toolsets)} toolset, "
                     f"{len(self._aktif)} aktif")

    def listele(self) -> list[dict]:
        """Tum toolset'leri listele."""
        return [
            {
                "ad": ad,
                "aciklama": bilgi["aciklama"],
                "aktif": ad in self._aktif,
                "arac_sayisi": len(bilgi.get("araclar", [])),
            }
            for ad, bilgi in self._toolsets.items()
        ]

    def aktif_toolsets(self) -> list[str]:
        """Aktif toolset adlarini don."""
        return sorted(self._aktif)

    def aktif_araclar(self) -> list[str]:
        """Aktif toolset'lerdeki tum arac adlarini don."""
        araclar = []
        for ad in self._aktif:
            bilgi = self._toolsets.get(ad, {})
            araclar.extend(bilgi.get("araclar", []))
        return sorted(set(araclar))

    def etkinlestir(self, ad: str) -> str:
        """Bir toolset'i etkinlestir."""
        if ad not in self._toolsets:
            mevcut = ", ".join(self._toolsets.keys())
            return f"[Toolset] '{ad}' bulunamadi. Mevcut: {mevcut}"
        self._aktif.add(ad)
        return f"[Toolset] '{ad}' etkinlestirildi"

    def devre_disi_birak(self, ad: str) -> str:
        """Bir toolset'i devre disi birak."""
        if ad not in self._toolsets:
            mevcut = ", ".join(self._toolsets.keys())
            return f"[Toolset] '{ad}' bulunamadi. Mevcut: {mevcut}"
        self._aktif.discard(ad)
        return f"[Toolset] '{ad}' devre disi birakildi"

    def komut_islem(self, args: str = "") -> str:
        """/tools komutunu isle.

        Kullanim:
          /tools                    -> Liste
          /tools ac <ad>           -> Etkinlestir
          /tools kapat <ad>        -> Devre disi birak
        """
        if not args or args.lower() in ("list", "liste", ""):
            satirlar = ["ReYMeN Toolsets:"]
            for ts in self.listele():
                isaret = "✅" if ts["aktif"] else "❌"
                satirlar.append(
                    f"  {isaret} {ts['ad']}: {ts['aciklama']} "
                    f"({ts['arac_sayisi']} arac)"
                )
            satirlar.append("")
            satirlar.append(
                "Kullanim: /tools ac <ad> | /tools kapat <ad>"
            )
            return "\n".join(satirlar)

        parts = args.strip().split(maxsplit=1)
        alt_komut = parts[0].lower()
        alt_args = parts[1] if len(parts) > 1 else ""

        if alt_komut == "ac":
            return self.etkinlestir(alt_args)
        if alt_komut == "kapat":
            return self.devre_disi_birak(alt_args)
        if alt_komut == "aktif":
            arac = self.aktif_araclar()
            return f"Aktif araclar ({len(arac)}): {', '.join(arac[:10])}..."

        return f"[Toolset] Bilinmeyen komut: {alt_komut}"

    def ping(self) -> bool:
        return True


# ── Singleton ─────────────────────────────────────────────────────

_toolset_instance: Optional[ToolsetManager] = None


def toolset_manager(config: Optional[dict] = None) -> ToolsetManager:
    global _toolset_instance
    if _toolset_instance is None:
        _toolset_instance = ToolsetManager(config)
    return _toolset_instance
