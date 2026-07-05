# -*- coding: utf-8 -*-
"""reymen/mcp/mcp_tool.py â€” MCP Araç KaydÄ± ve Ã‡aÄŸrÄ± FonksiyonlarÄ±.

ReYMeN Motor'una MCP_TOOL_LISTELE / MCP_TOOL_CAGIR fonksiyonlarÄ±nÄ± kaydeder.
reymen.arac.mcp_client_tool altyapÄ±sÄ±nÄ± kullanÄ±r (canlÄ± stdio/HTTP MCP client).

DoÄŸrudan da kullanÄ±labilir:

    from reymen.mcp.mcp_tool import mcp_tool_cagir, mcp_tool_listele

    tools = mcp_tool_listele()
    sonuc = mcp_tool_cagir("github", "issues/list", {"repo": "user/repo"})
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from reymen.arac.mcp_client_tool import (
    mcp_client_baglan,
    mcp_client_arac_cagir,
    mcp_client,
)

logger = logging.getLogger(__name__)

# BaÄŸlantÄ± önbelleÄŸi â€” ilk çaÄŸrÄ±da tüm config'deki sunuculara baÄŸlanÄ±r
_initialized = False


def _ensure_connected():
    """Tüm config'deki MCP sunucularÄ±na baÄŸlan (bir kere)."""
    global _initialized
    if _initialized:
        return
    yonetici = mcp_client()
    for ad in list(yonetici._konfig.keys()):
        try:
            yonetici._sunucu_al(ad)
        except Exception as e:
            logger.warning("MCP [%s] baÄŸlanamadÄ±: %s", ad, e)
    _initialized = True


def mcp_tool_listele(sunucu_ad: str = "") -> list[dict]:
    """Belirtilen sunucudaki veya tüm MCP araçlarÄ±nÄ± listele.

    Args:
        sunucu_ad: BoÅŸ = tüm sunucular, dolu = sadece o sunucu

    Returns:
        [{"sunucu", "name", "description"}, ...]
    """
    _ensure_connected()
    yonetici = mcp_client()
    tum = []
    for ad, araclar in yonetici.tum_araclar().items():
        for arac in araclar:
            tum.append(
                {
                    "sunucu": ad,
                    "name": arac.get("name", "?"),
                    "description": arac.get("description", ""),
                    "inputSchema": arac.get("inputSchema", {}),
                }
            )
    if sunucu_ad:
        tum = [a for a in tum if a["sunucu"] == sunucu_ad]
    return tum


def mcp_tool_cagir(sunucu: str, arac: str, args: Optional[dict] = None) -> str:
    """MCP sunucusunda bir aracÄ± çaÄŸÄ±r.

    Args:
        sunucu: MCP sunucu adÄ±
        arac: Ã‡aÄŸrÄ±lacak araç
        args: Parametreler

    Returns:
        AracÄ±n döndürdüÄŸü metin içerik
    """
    _ensure_connected()
    return mcp_client_arac_cagir(sunucu, arac, **(args or {}))


def motor_kaydet(motor) -> None:
    """MCP araçlarÄ±nÄ± Motor'a kaydet.

    Motor baÅŸlatÄ±lÄ±rken çaÄŸrÄ±lÄ±r.
    """
    _ensure_connected()
    if not hasattr(motor, "_plugin_arac_kaydet"):
        logger.warning("Motor'da _plugin_arac_kaydet metodu yok")
        return

    yonetici = mcp_client()
    yonetici.motor_kaydet(motor)

    # AyrÄ±ca genel liste/çaÄŸrÄ± fonksiyonlarÄ±nÄ± kaydet
    motor._plugin_arac_kaydet(
        "MCP_TOOL_LISTELE",
        mcp_tool_listele,
        "MCP sunucularÄ±ndaki araçlarÄ± listeler. "
        "KullanÄ±m: MCP_TOOL_LISTELE(sunucu_ad='')",
    )
    motor._plugin_arac_kaydet(
        "MCP_TOOL_CAGIR",
        mcp_tool_cagir,
        "MCP sunucusunda araç çaÄŸÄ±rÄ±r. "
        "KullanÄ±m: MCP_TOOL_CAGIR(sunucu='github', "
        "arac='issues/list', args={'repo': 'user/repo'})",
    )
