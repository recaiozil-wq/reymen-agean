# -*- coding: utf-8 -*-
"""
reymen/mcp/__init__.py â€” ReYMeN MCP Ä°stemci Paketi.

Model Context Protocol (MCP) sunucularÄ±na baÄŸlanma, tool keÅŸfetme ve Ã§aÄŸÄ±rma.

Alt ModÃ¼ller:
  mcp_manager      â€” Async MCP yÃ¶neticisi (singleton)
  mcp_tool         â€” Motor araÃ§ kaydÄ± (MCP_TOOL_LISTELE / MCP_TOOL_CAGIR)
  mcp_catalog      â€” Ã–nceden tanÄ±mlÄ± MCP sunucu kataloÄŸu
  mcp_discovery    â€” config.yaml + .env'den otomatik keÅŸif (MCP_DISCOVERY)
  mcp_reconnect    â€” Heartbeat + otomatik yeniden baÄŸlanma (MCP_RECONNECT_*)

KullanÄ±m:
    from reymen.mcp.mcp_manager import mcp_manager
    from reymen.mcp.mcp_discovery import mcp_kesfet
    from reymen.mcp.mcp_reconnect import mcp_reconnect_baslat

    # Otomatik keÅŸif
    yeni = mcp_kesfet()

    # BaÅŸlat ve keÅŸfet
    await mcp_manager().baslat()

    # Heartbeat + reconnect baÅŸlat
    await mcp_reconnect_baslat()

    # Tool Ã§aÄŸÄ±r
    sonuc = await mcp_manager().cagir("github", "issues/list", {"repo": "user/repo"})

    # TÃ¼m tool'larÄ± listele
    tools = mcp_manager().tum_araclari_getir()
"""

import asyncio
import logging
import sys

from reymen.mcp.mcp_tool import motor_kaydet as mcp_tool_kaydet
from reymen.mcp.mcp_discovery import motor_kaydet as mcp_discovery_kaydet
from reymen.mcp.mcp_reconnect import motor_kaydet as mcp_reconnect_kaydet
from reymen.mcp.mcp_discovery import mcp_kesfet
from reymen.mcp.mcp_reconnect import mcp_reconnect_baslat, mcp_reconnect_durumu

logger = logging.getLogger(__name__)

__all__ = [
    "mcp_tool_kaydet",
    "mcp_discovery_kaydet",
    "mcp_reconnect_kaydet",
    "baslangicta_baslat",
    "otomatik_kesif_yap",
    "_cift_mcp_uyar",
]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ModÃ¼l seviyesinde otomatik keÅŸif (motor._plugin_moduller_yukle() sÄ±rasÄ±nda)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def otomatik_kesif_yap() -> int:
    """ModÃ¼l import edildiÄŸinde MCP sunucularÄ±nÄ± otomatik keÅŸfeder.

    Motor._plugin_moduller_yukle() akÄ±ÅŸÄ±na entegredir:
      "reymen.mcp" import edildiÄŸinde bu fonksiyon Ã§aÄŸrÄ±lÄ±r,
      config.yaml + .env + ReYMeN profilinden MCP sunucularÄ±nÄ± bulur
      ve mcp_manager'a otomatik kaydeder.

    Returns:
        Yeni bulunan MCP sunucu sayÄ±sÄ±
    """
    try:
        yeni = mcp_kesfet(geri_bildirim=True)
        if yeni > 0:
            logger.info(
                "[MCP] Otomatik keÅŸif: %d yeni sunucu bulundu (modÃ¼l import)", yeni
            )
        return yeni
    except Exception as e:
        logger.debug("[MCP] Otomatik keÅŸif hatasÄ± (modÃ¼l import): %s", e)
        return 0


# ModÃ¼l import edildiÄŸinde otomatik keÅŸif Ã§alÄ±ÅŸtÄ±r
_otomatik_kesif_sonuc = otomatik_kesif_yap()


def _cift_mcp_uyar() -> None:
    """reymen.arac.native_mcp_client import edilmisse uyar (Ã§ift MCP client)."""
    try:
        if "reymen.arac.native_mcp_client" in sys.modules:
            logger.warning(
                "[MCP] âš ï¸ Ã‡ift MCP client tespit edildi! "
                "reymen.mcp ve reymen.arac.native_mcp_client paralel Ã§alÄ±ÅŸÄ±yor. "
                "Yeni geliÅŸtirmeler iÃ§in reymen.mcp paketini kullanÄ±n."
            )
    except Exception as _e:
        __import__("logging").getLogger(__name__).warning(
            "[SessizExcept] %%s: %%s", type(_e).__name__, _e
        )


def baslangicta_baslat() -> None:
    """Motor yÃ¼klenirken otomatik MCP keÅŸif ve reconnect baÅŸlat.

    Motor baÅŸlatÄ±lÄ±rken motor_kaydet() iÃ§inden Ã§aÄŸrÄ±lÄ±r:
      1. config.yaml + .env'den MCP sunucularÄ±nÄ± keÅŸfeder
      2. Heartbeat + otomatik yeniden baÄŸlanma dÃ¶ngÃ¼sÃ¼nÃ¼ baÅŸlatÄ±r

    Hata varsa sessizce logla, crash yapma. HalihazÄ±rda reconnect
    Ã§alÄ±ÅŸÄ±yorsa ikinci kez baÅŸlatma yapÄ±lmaz.
    """
    try:
        # HalihazÄ±rda reconnect Ã§alÄ±ÅŸÄ±yorsa atla
        if mcp_reconnect_durumu().get("aktif", False):
            logger.debug("[MCP] baslangicta_baslat: reconnect zaten Ã§alÄ±ÅŸÄ±yor")
            return

        # 1. MCP sunucularÄ±nÄ± keÅŸfet
        yeni = mcp_kesfet(geri_bildirim=True)
        if yeni > 0:
            logger.info("[MCP] Baslangicta kesif: %d yeni sunucu bulundu", yeni)

        # 2. Reconnect baÅŸlat
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(mcp_reconnect_baslat())
                logger.info("[MCP] Baslangicta reconnect baslatildi")
            finally:
                loop.close()
        except Exception as e:
            logger.warning(
                "[MCP] Baslangicta reconnect baslatma hatasi (onemsiz): %s", e
            )
    except Exception as e:
        logger.warning("[MCP] Baslangicta baslatma hatasi (onemsiz): %s", e)


def motor_kaydet(motor) -> None:
    """TÃ¼m MCP araÃ§larÄ±nÄ± Motor'a kaydet.

    Motor baÅŸlatÄ±lÄ±rken Ã§aÄŸrÄ±lÄ±r. SÄ±rasÄ±yla:
      1. Ã‡ift MCP client uyarÄ±sÄ± (_cift_mcp_uyar)
      2. MCP_TOOL_LISTELE / MCP_TOOL_CAGIR (mcp_tool)
      3. MCP_DISCOVERY / MCP_DISCOVERY_DURUM (mcp_discovery)
      4. MCP_RECONNECT_BASLAT / MCP_RECONNECT_DURDUR / MCP_RECONNECT_DURUM (mcp_reconnect)
      5. MCP_OTOMATIK_BASLAT â€” keÅŸif + reconnect'i tek adÄ±mda baÅŸlatÄ±r
    """
    # Ã‡ift MCP client uyarÄ±sÄ±
    _cift_mcp_uyar()

    # Alt modÃ¼l araÃ§larÄ±nÄ± kaydet
    mcp_tool_kaydet(motor)
    mcp_discovery_kaydet(motor)
    mcp_reconnect_kaydet(motor)

    # MCP_OTOMATIK_BASLAT â€” motor baÅŸlangÄ±cÄ±nda Ã§aÄŸrÄ±lacak auto-start tool
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "MCP_OTOMATIK_BASLAT",
            baslangicta_baslat,
            "MCP sunucularÄ±nÄ± otomatik keÅŸfeder, heartbeat + yeniden baÄŸlanma "
            "dÃ¶ngÃ¼sÃ¼nÃ¼ baÅŸlatÄ±r. Motor baÅŸlangÄ±cÄ±nda otomatik Ã§aÄŸrÄ±lÄ±r. "
            "KullanÄ±m: MCP_OTOMATIK_BASLAT() â€” keÅŸif + reconnect tek adÄ±mda.",
        )
