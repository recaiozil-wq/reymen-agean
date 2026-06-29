# -*- coding: utf-8 -*-
"""reymen/mcp/mcp_tool.py — MCP Araç Kaydı ve Çağrı Fonksiyonları.

ReYMeN Motor'una MCP_TOOL_LISTELE / MCP_TOOL_CAGIR fonksiyonlarını kaydeder.
Doğrudan da kullanılabilir:

    from reymen.mcp.mcp_tool import mcp_tool_cagir, mcp_tool_listele

    tools = mcp_tool_listele()
    sonuc = mcp_tool_cagir("github", "issues/list", {"repo": "user/repo"})
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from reymen.mcp.mcp_manager import mcp_manager

logger = logging.getLogger(__name__)


def mcp_tool_listele(sunucu_ad: str = "") -> list[dict]:
    """Belirtilen sunucudaki veya tüm MCP araçlarını listele.

    Args:
        sunucu_ad: Boş = tüm sunucular, dolu = sadece o sunucu

    Returns:
        [{"sunucu", "name", "description"}, ...]
    """
    mgr = mcp_manager()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if not mgr._basladi:
            loop.run_until_complete(mgr.baslat())
        tum = mgr.tum_araclari_getir()
        if sunucu_ad:
            tum = [a for a in tum if a["sunucu"] == sunucu_ad]
        return tum
    except Exception as e:
        logger.error("MCP araç listeleme hatası: %s", e)
        return []
    finally:
        loop.close()


def mcp_tool_cagir(
    sunucu: str, arac: str, args: Optional[dict] = None
) -> str:
    """MCP sunucusunda bir aracı çağır.

    Args:
        sunucu: MCP sunucu adı
        arac: Çağrılacak araç
        args: Parametreler

    Returns:
        Aracın döndürdüğü metin içerik
    """
    mgr = mcp_manager()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if not mgr._basladi:
            loop.run_until_complete(mgr.baslat())
        sonuc = loop.run_until_complete(mgr.cagir(sunucu, arac, args))
        if sonuc.get("durum") == "hata":
            return f"HATA: {sonuc.get('hata', 'bilinmeyen hata')}"
        return sonuc.get("icerik", "")
    except Exception as e:
        logger.error("MCP çağrı hatası: %s", e)
        return f"HATA: {e}"
    finally:
        loop.close()


def motor_kaydet(motor) -> None:
    """MCP araçlarını Motor'a kaydet.

    Motor başlatılırken çağrılır.
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        logger.warning("Motor'da _plugin_arac_kaydet metodu yok")
        return

    motor._plugin_arac_kaydet(
        "MCP_TOOL_LISTELE",
        mcp_tool_listele,
        "MCP sunucularındaki araçları listeler. "
        "Kullanım: MCP_TOOL_LISTELE(sunucu_ad='')",
    )
    motor._plugin_arac_kaydet(
        "MCP_TOOL_CAGIR",
        mcp_tool_cagir,
        "MCP sunucusunda araç çağırır. "
        "Kullanım: MCP_TOOL_CAGIR(sunucu='github', "
        "arac='issues/list', args={'repo': 'user/repo'})",
    )
