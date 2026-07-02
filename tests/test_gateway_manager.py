# -*- coding: utf-8 -*-
"""test_gateway_manager.py — GatewayYoneticisi birim testleri (yüzeyel geçiş)."""

import pytest

from src.core.gateway_manager import CLIAdapter, GatewayYoneticisi


# ── Happy Path ──────────────────────────────────────────────────────────


class TestGatewayKaydet:
    """Adapter kaydetme işlemleri."""

    def test_kaydet_basarili(self):
        """CLIAdapter kaydetme → başarılı, listede görünür."""
        yonetici = GatewayYoneticisi()
        sonuc = yonetici.kaydet(CLIAdapter())
        assert sonuc is True
        assert len(yonetici.liste()) == 1
        assert yonetici.liste()[0]["ad"] == "cli"

    def test_kaydet_gecersiz_tip(self):
        """Geçersiz adapter tipi → False döner."""
        yonetici = GatewayYoneticisi()
        sonuc = yonetici.kaydet("ben_bir_stringim")  # type: ignore
        assert sonuc is False


class TestGatewayMesajGonder:
    """Mesaj gönderim işlemleri."""

    @pytest.mark.asyncio
    async def test_mesaj_gonder_cli_basarili(self, capsys):
        """CLI platformuna mesaj gönderimi → başarılı, stdout'a yazılır."""
        yonetici = GatewayYoneticisi()
        yonetici.kaydet(CLIAdapter())
        await yonetici.baslat("cli")

        sonuc = await yonetici.mesaj_gonder("cli", "Merhaba test!")
        assert sonuc["basarili"] is True
        assert sonuc["platform"] == "cli"

        captured = capsys.readouterr()
        assert "Merhaba test!" in captured.out

        await yonetici.hepsini_durdur()

    @pytest.mark.asyncio
    async def test_mesaj_gonder_bilinmeyen_platform(self):
        """Var olmayan platform → hata döner."""
        yonetici = GatewayYoneticisi()
        yonetici.kaydet(CLIAdapter())
        await yonetici.baslat("cli")

        sonuc = await yonetici.mesaj_gonder("mars", "Yetkilendirme yapildi mi?")
        assert sonuc["basarili"] is False
        assert "bulunamadi" in sonuc["hata"]
        assert "mars" in sonuc["hata"]

        await yonetici.hepsini_durdur()


class TestGatewayListe:
    """Gateway listeleme işlemleri."""

    def test_liste_bos_iken(self):
        """Hiç adapter yokken liste boş döner."""
        yonetici = GatewayYoneticisi()
        assert yonetici.liste() == []
