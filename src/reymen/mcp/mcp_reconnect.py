# -*- coding: utf-8 -*-
"""
reymen/mcp/mcp_reconnect.py â€” MCP BaÄŸlantÄ± Testi ve Otomatik Yeniden BaÄŸlanma ModÃ¼lÃ¼.

TÃ¼m MCP sunucu baÄŸlantÄ±larÄ±nÄ± periyodik olarak kontrol eder:
  - Her 30 saniyede bir heartbeat (tools/list) gÃ¶nderir
  - Kopan baÄŸlantÄ±larÄ± exponential backoff ile yeniden baÄŸlar (max 5 deneme)
  - Durumu raporlar

KullanÄ±m:
    from reymen.mcp.mcp_reconnect import mcp_reconnect_baslat, mcp_reconnect_durdur

    # Arkaplanda heartbeat + reconnect baÅŸlat
    await mcp_reconnect_baslat()

    # Durum raporu
    rapor = mcp_reconnect_durum_raporu()
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Optional

from reymen.mcp.mcp_manager import mcp_manager, MCPServerBaglantisi

logger = logging.getLogger(__name__)

# â”€â”€ VarsayÄ±lan ayarlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
HEARTBEAT_ARALIK_SN = 30  # Her N saniyede bir heartbeat
MAX_YENIDEN_DENEME = 5  # Maksimum yeniden baÄŸlanma denemesi
MAX_BACKOFF_SN = 60  # Maksimum bekleme sÃ¼resi (exponential backoff)

# â”€â”€ Global state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_reconnect_gorev: Optional[asyncio.Task] = None
_durduruldu = False
_durum: dict[str, Any] = {
    "aktif": False,
    "heartbeat_sayisi": 0,
    "yeniden_baglanma_sayisi": 0,
    "hata_sayisi": 0,
    "baslangic_zamani": None,
    "sunucu_durumlari": {},
}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Heartbeat â€” Her MCP Sunucusuna Periyodik Sinyal
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


async def _heartbeat_gonder(
    baglanti: MCPServerBaglantisi,
) -> bool:
    """Tek bir MCP sunucusuna heartbeat (tools/list) gÃ¶nder.

    Returns:
        True = baÅŸarÄ±lÄ±, False = baÅŸarÄ±sÄ±z / baÄŸlantÄ± koptu.
    """
    try:
        istek = {"jsonrpc": "2.0", "id": 0, "method": "tools/list"}
        sonuc = await baglanti._gonder(istek)
        if "error" in sonuc:
            logger.warning("MCP Heartbeat [%s]: hata %s", baglanti.ad, sonuc["error"])
            return False
        baglanti._baglandi = True
        return True
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.debug("MCP Heartbeat [%s]: %s", baglanti.ad, e)
        return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Yeniden BaÄŸlanma â€” Exponential Backoff ile
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


async def _yeniden_baglan(
    baglanti: MCPServerBaglantisi,
    deneme: int,
) -> bool:
    """Exponential backoff ile bir MCP sunucusuna yeniden baÄŸlan.

    Args:
        baglanti: Yeniden baÄŸlanÄ±lacak MCP sunucu baÄŸlantÄ±sÄ±
        deneme: Mevcut deneme sayÄ±sÄ± (0-indexed)

    Returns:
        True = baÅŸarÄ±lÄ±, False = tÃ¼m denemeler baÅŸarÄ±sÄ±z
    """
    bekle_sn = min(2 ** (deneme + 1), MAX_BACKOFF_SN)
    logger.info(
        "MCP Yeniden BaÄŸlanma [%s]: deneme %d/%d, %ds bekleniyor...",
        baglanti.ad,
        deneme + 1,
        MAX_YENIDEN_DENEME,
        bekle_sn,
    )
    try:
        await asyncio.sleep(bekle_sn)
    except asyncio.CancelledError:
        return False

    try:
        # tools/list ile keÅŸif yap (baÄŸlantÄ±yÄ± test et)
        istek = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        sonuc = await baglanti._gonder(istek)
        if "error" in sonuc:
            logger.warning(
                "MCP Yeniden BaÄŸlanma [%s]: deneme %d baÅŸarÄ±sÄ±z: %s",
                baglanti.ad,
                deneme + 1,
                sonuc["error"],
            )
            return False

        # BaÅŸarÄ±lÄ± â†’ araÃ§ listesini gÃ¼ncelle
        tools = sonuc.get("result", {}).get("tools", [])
        baglanti._tools = tools
        baglanti._baglandi = True
        logger.info(
            "MCP Yeniden BaÄŸlanma [%s]: baÅŸarÄ±lÄ± (%d tool)",
            baglanti.ad,
            len(tools),
        )
        return True

    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.warning(
            "MCP Yeniden BaÄŸlanma [%s]: deneme %d istisna: %s",
            baglanti.ad,
            deneme + 1,
            e,
        )
        return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ana DÃ¶ngÃ¼ â€” Heartbeat + Reconnect
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


async def _reconnect_dongusu() -> None:
    """Heartbeat ve yeniden baÄŸlanma ana dÃ¶ngÃ¼sÃ¼.

    Her HEARTBEAT_ARALIK_SN saniyede bir tÃ¼m MCP sunucularÄ±na heartbeat gÃ¶nderir.
    BaÅŸarÄ±sÄ±z olanlarÄ± exponential backoff ile yeniden baÄŸlamayÄ± dener.
    """
    global _durum

    mgr = mcp_manager()
    _durum["aktif"] = True
    _durum["baslangic_zamani"] = time.time()

    logger.info(
        "MCP Reconnect: heartbeat dÃ¶ngÃ¼sÃ¼ baÅŸladÄ± (aralÄ±k: %ds)", HEARTBEAT_ARALIK_SN
    )

    try:
        while not _durduruldu:
            sunucu_listesi = list(mgr._sunucular.items())

            if not sunucu_listesi:
                await asyncio.sleep(HEARTBEAT_ARALIK_SN)
                continue

            for ad, baglanti in sunucu_listesi:
                if _durduruldu:
                    break

                # Sunucu durumunu izle
                if ad not in _durum["sunucu_durumlari"]:
                    _durum["sunucu_durumlari"][ad] = {
                        "bagli": False,
                        "son_heartbeat": None,
                        "son_hata": None,
                        "yeniden_baglanma_sayisi": 0,
                        "hata_sayisi": 0,
                    }

                sd = _durum["sunucu_durumlari"][ad]

                # Heartbeat gÃ¶nder
                basarili = await _heartbeat_gonder(baglanti)
                _durum["heartbeat_sayisi"] += 1

                if basarili:
                    sd["bagli"] = True
                    sd["son_heartbeat"] = time.time()
                    sd["son_hata"] = None
                    # Yeniden baÄŸlanma denemelerini sÄ±fÄ±rla (baÅŸarÄ±lÄ± heartbeat)
                    sd["yeniden_baglanma_sayisi"] = 0
                else:
                    sd["bagli"] = False
                    sd["son_hata"] = time.time()
                    sd["hata_sayisi"] += 1
                    _durum["hata_sayisi"] += 1

                    # BaÄŸlantÄ± koptu â†’ exponential backoff ile yeniden baÄŸlan
                    deneme = 0
                    while deneme < MAX_YENIDEN_DENEME and not _durduruldu:
                        basarili_mi = await _yeniden_baglan(baglanti, deneme)
                        if basarili_mi:
                            _durum["yeniden_baglanma_sayisi"] += 1
                            sd["yeniden_baglanma_sayisi"] += 1
                            sd["bagli"] = True
                            sd["son_hata"] = None
                            break
                        deneme += 1

                    if not sd["bagli"] and deneme >= MAX_YENIDEN_DENEME:
                        logger.error(
                            "MCP Reconnect [%s]: %d deneme sonunda baÄŸlanamadÄ±, "
                            "manuel mÃ¼dahale gerekebilir",
                            ad,
                            MAX_YENIDEN_DENEME,
                        )

            # Belirtilen aralÄ±k kadar bekle
            await asyncio.sleep(HEARTBEAT_ARALIK_SN)

    except asyncio.CancelledError:
        logger.info("MCP Reconnect: dÃ¶ngÃ¼ iptal edildi")
    except Exception as e:
        logger.warning("MCP Reconnect: dÃ¶ngÃ¼ hatasÄ±: %s", e)
    finally:
        _durum["aktif"] = False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Public API â€” BaÅŸlat / Durdur / Durum
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


async def mcp_reconnect_baslat() -> bool:
    """Heartbeat + yeniden baÄŸlanma dÃ¶ngÃ¼sÃ¼nÃ¼ baÅŸlat.

    Returns:
        True = baÅŸlatÄ±ldÄ±, False = zaten Ã§alÄ±ÅŸÄ±yor.
    """
    global _reconnect_gorev, _durduruldu

    if _reconnect_gorev is not None and not _reconnect_gorev.done():
        logger.info("MCP Reconnect: zaten Ã§alÄ±ÅŸÄ±yor")
        return False

    _durduruldu = False
    _reconnect_gorev = asyncio.create_task(_reconnect_dongusu())
    logger.info("MCP Reconnect: baÅŸlatÄ±ldÄ±")
    return True


def mcp_reconnect_durdur() -> None:
    """Heartbeat + yeniden baÄŸlanma dÃ¶ngÃ¼sÃ¼nÃ¼ durdur."""
    global _durduruldu

    _durduruldu = True
    if _reconnect_gorev is not None and not _reconnect_gorev.done():
        _reconnect_gorev.cancel()
    _durum["aktif"] = False
    logger.info("MCP Reconnect: durduruldu")


def mcp_reconnect_durumu() -> dict[str, Any]:
    """Reconnect sisteminin mevcut durumunu dÃ¶ndÃ¼r.

    Returns:
        {
            "aktif": bool,
            "heartbeat_sayisi": int,
            "yeniden_baglanma_sayisi": int,
            "hata_sayisi": int,
            "calisma_suresi_sn": float,
            "sunucular": {
                "sunucu_adi": {
                    "bagli": bool,
                    "son_heartbeat": float|None,
                    "son_hata": float|None,
                    "yeniden_baglanma_sayisi": int,
                    "hata_sayisi": int,
                }
            }
        }
    """
    global _durum
    su_an = time.time()
    baslangic = _durum.get("baslangic_zamani")
    calisma_suresi = su_an - baslangic if baslangic else 0.0

    return {
        "aktif": _durum.get("aktif", False),
        "heartbeat_sayisi": _durum.get("heartbeat_sayisi", 0),
        "yeniden_baglanma_sayisi": _durum.get("yeniden_baglanma_sayisi", 0),
        "hata_sayisi": _durum.get("hata_sayisi", 0),
        "calisma_suresi_sn": round(calisma_suresi, 1),
        "sunucular": dict(_durum.get("sunucu_durumlari", {})),
    }


def mcp_reconnect_durum_raporu() -> str:
    """Ä°nsan-okunabilir reconnect durum raporu."""
    durum = mcp_reconnect_durumu()
    aktif_str = "ğŸŸ¢ Ã‡alÄ±ÅŸÄ±yor" if durum["aktif"] else "ğŸ”´ Durduruldu"
    sure_str = (
        f"{durum['calisma_suresi_sn']:.0f}s" if durum["calisma_suresi_sn"] > 0 else "-"
    )

    satirlar = [
        "[MCP Reconnect] BaÄŸlantÄ± Ä°zleme Raporu",
        "=" * 50,
        f"  Durum: {aktif_str}",
        f"  Ã‡alÄ±ÅŸma SÃ¼resi: {sure_str}",
        f"  Heartbeat: {durum['heartbeat_sayisi']}",
        f"  Yeniden BaÄŸlanma: {durum['yeniden_baglanma_sayisi']}",
        f"  Hata: {durum['hata_sayisi']}",
        "",
        "  Sunucular:",
    ]

    if not durum["sunucular"]:
        satirlar.append("    (izlenen sunucu yok)")
    else:
        for ad, sd in durum["sunucular"].items():
            simge = "ğŸŸ¢" if sd["bagli"] else "ğŸ”´"
            son_hb = (
                f"{(time.time() - sd['son_heartbeat']):.0f}s Ã¶nce"
                if sd["son_heartbeat"]
                else "hiÃ§"
            )
            satirlar.append(
                f"    {simge} {ad}: son heartbeat {son_hb}, "
                f"yeniden baÄŸlanma {sd['yeniden_baglanma_sayisi']}, "
                f"hata {sd['hata_sayisi']}"
            )

    return "\n".join(satirlar)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Motor Tool KaydÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def motor_kaydet(motor) -> None:
    """MCP_RECONNECT araÃ§larÄ±nÄ± Motor'a kaydet.

    Motor baÅŸlatÄ±lÄ±rken Ã§aÄŸrÄ±lÄ±r.
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        logger.warning("Motor'da _plugin_arac_kaydet metodu yok")
        return

    motor._plugin_arac_kaydet(
        "MCP_RECONNECT_BASLAT",
        _mcp_reconnect_baslat_sync,
        "MCP sunucularÄ±na periyodik heartbeat (30sn) gÃ¶ndermeyi ve "
        "kopan baÄŸlantÄ±larÄ± otomatik yeniden baÄŸlamayÄ± baÅŸlatÄ±r. "
        "KullanÄ±m: MCP_RECONNECT_BASLAT()",
    )

    motor._plugin_arac_kaydet(
        "MCP_RECONNECT_DURDUR",
        mcp_reconnect_durdur,
        "MCP heartbeat/yeniden baÄŸlanma dÃ¶ngÃ¼sÃ¼nÃ¼ durdurur. "
        "KullanÄ±m: MCP_RECONNECT_DURDUR()",
    )

    motor._plugin_arac_kaydet(
        "MCP_RECONNECT_DURUM",
        mcp_reconnect_durum_raporu,
        "MCP baÄŸlantÄ± izleme sisteminin durum raporunu dÃ¶ndÃ¼rÃ¼r. "
        "KullanÄ±m: MCP_RECONNECT_DURUM()",
    )


def _mcp_reconnect_baslat_sync() -> str:
    """Senkron wrapper for mcp_reconnect_baslat."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(mcp_reconnect_baslat())
            return "[MCP Reconnect] BaÅŸlatÄ±ldÄ±"
        finally:
            loop.close()
    except Exception as e:
        return f"[MCP Reconnect] Hata: {e}"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CLI Test
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    import time

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    print("=== MCP Reconnect Test ===\n")

    async def test():
        # Ã–nce keÅŸif yap
        from reymen.mcp.mcp_discovery import mcp_kesfet

        eklenen = mcp_kesfet()
        print(f"KeÅŸfedilen sunucu: {eklenen}")

        # Reconnect baÅŸlat
        baslatildi = await mcp_reconnect_baslat()
        print(f"Reconnect baÅŸlatÄ±ldÄ±: {baslatildi}")

        # 5 saniye bekle (birkaÃ§ heartbeat)
        print("\n5 saniye bekleniyor...")
        await asyncio.sleep(5)

        # Durum raporu
        print(f"\n{mcp_reconnect_durum_raporu()}")

        # Durdur
        mcp_reconnect_durdur()
        print("\nâ†’ Reconnect durduruldu")

    asyncio.run(test())
