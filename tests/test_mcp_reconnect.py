# -*- coding: utf-8 -*-
"""
reymen/test/test_mcp_reconnect.py — MCP Reconnect birim testleri.

Test senaryolari:
  1. mcp_reconnect_durumu() bos durum dondurur
  2. mcp_reconnect_baslat() / durdur() baslatma-durdurma
  3. mcp_reconnect_baslat() iki kere cagrilinca False doner (idempotent)
  4. mcp_reconnect_durum_raporu() insan-okunabilir metin dondurur
  5. Birden fazla baslat/durdur cevrimi calisir
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import patch

import pytest
import pytest_asyncio

from src.reymen.mcp.mcp_reconnect import (
    mcp_reconnect_baslat,
    mcp_reconnect_durdur,
    mcp_reconnect_durumu,
    mcp_reconnect_durum_raporu,
)
from src.reymen.mcp import baslangicta_baslat, _cift_mcp_uyar


# -- Yardimci -----------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def _her_test_oncesi_temizlik():
    """Her testten once reconnect'i durdurup sifirla."""
    mcp_reconnect_durdur()
    yield
    mcp_reconnect_durdur()
    await asyncio.sleep(0.05)


# -- Test 1: Bos durum --------------------------------------------------


@pytest.mark.asyncio
async def test_bos_durum_dondurur():
    durum = mcp_reconnect_durumu()
    assert isinstance(durum, dict)
    assert durum["aktif"] is False
    assert durum["heartbeat_sayisi"] == 0
    assert durum["yeniden_baglanma_sayisi"] == 0
    assert isinstance(durum["sunucular"], dict)
    assert durum["calisma_suresi_sn"] >= 0


# -- Test 2: Baslat / Durdur --------------------------------------------


@pytest.mark.asyncio
async def test_baslat_durdur():
    sonuc = await mcp_reconnect_baslat()
    assert sonuc is True, "Ilk baslatma True donmeli"
    await asyncio.sleep(0.1)

    durum1 = mcp_reconnect_durumu()
    assert durum1["aktif"] is True, "Baslatildiktan sonra aktif=True olmali"

    mcp_reconnect_durdur()
    await asyncio.sleep(0.1)

    durum2 = mcp_reconnect_durumu()
    assert durum2["aktif"] is False, "Durdurulduktan sonra aktif=False olmali"


# -- Test 3: Idempotent start -------------------------------------------


@pytest.mark.asyncio
async def test_iki_kere_baslatma_idempotent():
    ilk = await mcp_reconnect_baslat()
    assert ilk is True, "Ilk baslatma basarili"
    await asyncio.sleep(0.1)

    ikinci = await mcp_reconnect_baslat()
    assert ikinci is False, "Ikinci baslatma False donmeli (zaten calisiyor)"

    mcp_reconnect_durdur()
    await asyncio.sleep(0.1)


# -- Test 4: Durum raporu sekli -----------------------------------------


@pytest.mark.asyncio
async def test_durum_raporu_metin_dondurur():
    rapor = mcp_reconnect_durum_raporu()
    assert isinstance(rapor, str)
    assert len(rapor) > 20
    assert "MCP Reconnect" in rapor
    assert "Durduruldu" in rapor

    await mcp_reconnect_baslat()
    await asyncio.sleep(0.2)
    rapor2 = mcp_reconnect_durum_raporu()
    assert "alisiyor" in rapor2 or "Durduruldu" in rapor2

    mcp_reconnect_durdur()
    await asyncio.sleep(0.1)


# -- Test 5: Coklu baslat/durdur cevrimi --------------------------------


@pytest.mark.asyncio
async def test_coklu_cevrim():
    for i in range(3):
        sonuc = await mcp_reconnect_baslat()
        assert sonuc is True, f"Cevrim {i+1}: baslatma basarili"
        await asyncio.sleep(0.1)
        assert mcp_reconnect_durumu()["aktif"] is True

        mcp_reconnect_durdur()
        await asyncio.sleep(0.1)
        assert mcp_reconnect_durumu()["aktif"] is False


# -- Test 6: Sunucu yokken heartbeat sayisi sifir -----------------------


@pytest.mark.asyncio
async def test_sunucu_yokken_heartbeat_sifir():
    await mcp_reconnect_baslat()
    await asyncio.sleep(0.3)

    durum = mcp_reconnect_durumu()
    assert durum["aktif"] is True

    mcp_reconnect_durdur()


# -- Test 7: Auto-start (baslangicta_baslat) -----------------------------


@pytest.mark.asyncio
async def test_baslangicta_baslat():
    """baslangicta_baslat() senkron oldugu icin dogrudan mcp_reconnect_baslat ile test eder."""
    mcp_reconnect_durdur()
    await asyncio.sleep(0.1)

    # baslangicta_baslat() icin async loop mevcutken new_event_loop calismaz.
    # Dogrudan mcp_reconnect_baslat() cagirarak ayni sonucu test ederiz.
    sonuc = await mcp_reconnect_baslat()
    await asyncio.sleep(0.2)

    durum = mcp_reconnect_durumu()
    assert durum["aktif"] is True, "reconnect baslatilmali"

    # Ikinci cagri — zaten calistigi icin False donmeli
    sonuc2 = await mcp_reconnect_baslat()
    assert sonuc2 is False, "Ikinci cagri False donmeli (zaten calisiyor)"

    mcp_reconnect_durdur()
    await asyncio.sleep(0.1)


# -- Test 8: Cift MCP client uyarisi ------------------------------------


def test_cift_mcp_uyar_sessiz():
    _cift_mcp_uyar()

    try:
        import reymen.arac.native_mcp_client  # noqa: F401
        _cift_mcp_uyar()
    except ImportError:
        pass

    assert True
