#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mcp_tool.py — MCP Araci (ToolRegistry + Motor uyumlu).

ReYMeN'den MCP sunucularina baglanmak icin.
ToolRegistry tarafindan otomatik kesfedilir (run() fonksiyonu ile).
Motor'a _plugin_arac_kaydet ile kaydedilir (motor_kaydet() fonksiyonu ile).

Kullanim (ReYMeN icinde):
  MCP_CAGIR(sunucu="github", arac="issues/list", args={"repo": "user/repo"})
  MCP_TOOL_LISTELE()
  MCP_TOOL_CAGIR(sunucu="github", arac="issues/list", args={"repo": "user/repo"})
"""

import json
from typing import Any, Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("hermes.mcp_tool")
    logging.basicConfig(level=logging.INFO)

TOOL_META = {
    "aciklama": (
        "MCP (Model Context Protocol) sunucusuna baglanip arac cagirir. "
        "GitHub, dosya sistemi, veritabani gibi harici servislere erisir. "
        "Kullanim: MCP_CAGIR(sunucu='github', arac='issues/list', args={'repo': 'user/repo'})"
    ),
    "kategori": "entegrasyon",
    "parametreler": [
        {
            "ad": "sunucu",
            "tip": "str",
            "zorunlu": True,
            "aciklama": "MCP sunucu adi (config.yaml'daki mcp_servers anahtari)",
        },
        {
            "ad": "arac",
            "tip": "str",
            "zorunlu": True,
            "aciklama": "Cagrilacak MCP arac adi",
        },
        {
            "ad": "args",
            "tip": "dict",
            "zorunlu": False,
            "varsayilan": {},
            "aciklama": "Araca gonderilecek parametreler (JSON obje)",
        },
    ],
    "ornek": (
        'MCP_CAGIR(sunucu="github", arac="issues/list", '
        'args={"repo": "owner/repo"})'
    ),
}


def check_fn() -> bool:
    """En az bir MCP sunucusu yapilandirilmis mi?"""
    try:
        import yaml
        from pathlib import Path
        cfg_path = Path(__file__).parent.parent / "config.yaml"
        if not cfg_path.exists():
            return False
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        servers = cfg.get("mcp_servers") or {}
        return bool(servers)
    except Exception:
        return False


def run(sunucu: str, arac: str, args: Optional[dict] = None) -> dict:
    """
    MCP sunucusunda bir arac cagir.

    ToolRegistry uyumlu: tools/mcp_tool.py icinde run() fonksiyonu.
    """
    from tools.mcp_manager import mcp_manager
    import asyncio

    mgr = mcp_manager()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        if not mgr._basladi:
            arac_sayisi = loop.run_until_complete(mgr.baslat())
            logger.info(f"MCP: {arac_sayisi} arac kesfedildi")

        sonuc = loop.run_until_complete(mgr.cagir(sunucu, arac, args))
        return sonuc
    except Exception as e:
        logger.error(f"MCP cagri hatasi: {e}")
        return {"durum": "hata", "sunucu": sunucu, "arac": arac, "hata": str(e)}
    finally:
        loop.close()


# ── Motor entegrasyonu icin wrapper fonksiyonlar ───────────────────

def mcp_tool_listele(sunucu_ad: str = "") -> list[dict]:
    """Belirtilen sunucudaki veya tum MCP araclari listele.

    Args:
        sunucu_ad: Bos = tum sunucular, dolu = sadece o sunucu

    Returns:
        [{"sunucu", "name", "description"}, ...]
    """
    from tools.mcp_manager import mcp_manager
    import asyncio

    mgr = mcp_manager()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        if not mgr._basladi:
            loop.run_until_complete(mgr.baslat())

        tum_araclar = mgr.tum_araclari_getir()
        if sunucu_ad:
            tum_araclar = [a for a in tum_araclar if a["sunucu"] == sunucu_ad]
        return tum_araclar
    except Exception as e:
        logger.error(f"MCP arac listeleme hatasi: {e}")
        return []
    finally:
        loop.close()


def mcp_tool_cagir(sunucu: str, arac: str, args: Optional[dict] = None) -> str:
    """MCP sunucusunda bir araci cagir.

    Args:
        sunucu: MCP sunucu adi
        arac: Cagrilacak arac
        args: Parametreler

    Returns:
        Aracin dondurdugu metin icerik
    """
    sonuc = run(sunucu, arac, args)
    if sonuc.get("durum") == "hata":
        return f"HATA: {sonuc.get('hata', 'bilinmeyen hata')}"
    return sonuc.get("icerik", "")


def motor_kaydet(motor) -> None:
    """MCP tool'larini Motor'a kaydet.

    Cagri: motor.py baslatilirken cagrilir.
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        logger.warning("Motor'da _plugin_arac_kaydet metodu yok")
        return

    motor._plugin_arac_kaydet(
        "MCP_TOOL_LISTELE", mcp_tool_listele,
        "MCP sunucularindaki araclari listeler. "
        "Kullanim: MCP_TOOL_LISTELE(sunucu_ad='')"
    )
    motor._plugin_arac_kaydet(
        "MCP_TOOL_CAGIR", mcp_tool_cagir,
        "MCP sunucusunda arac cagirir. "
        "Kullanim: MCP_TOOL_CAGIR(sunucu='github', arac='issues/list', "
        "args={'repo': 'user/repo'})"
    )


# ── Upstream Hermes uyumluluk stublari ─────────────────────────────────


class MCPServerTask:
    """MCP Sunucu Gorevi — upstream Hermes uyumluluk katmani.

    MCP sunucu yonetimi icin task sinifi.
    """

    def __init__(self, server_name: str = "", config: Any = None):
        self.server_name = server_name
        self._config = config

    async def run(self):
        pass

    async def stop(self):
        pass


_servers: dict = {}
"""MCP sunucu kayitlari — upstream Hermes uyumluluk."""


class NonMcpEndpointError(Exception):
    """MCP endpoint hatasi — upstream Hermes uyumluluk."""
    pass


class CreateMessageResultWithTools:
    pass


class SamplingHandler:
    pass


LATEST_PROTOCOL_VERSION: str = "2025-03-26"
_DEFAULT_TOOL_TIMEOUT: float = 60.0
_MCP_AVAILABLE: bool = False
_existing_tool_names: set = set()


def _format_connect_error(e: Exception) -> str:
    return f"MCP baglanti hatasi: {e}"


def _resolve_stdio_command(cmd: str) -> list:
    return cmd.split() if cmd else []


def _snapshot_child_pids() -> list:
    return []
