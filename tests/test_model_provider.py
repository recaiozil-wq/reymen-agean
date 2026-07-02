# -*- coding: utf-8 -*-
"""Test: model_provider.py — ProviderChain + failover"""

import sys
import os

# Proje kokunu ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from src.core.model_provider import ProviderChain, ProviderKayit, CalistirSonuc, _provider_fabrikasi


class TestProviderChain:
    """ProviderChain: zincir olusturma, calistirma, durum raporu."""

    def test_zincir_olusturma(self):
        """Happy path: varsayilan zincirde 6 provider olmali."""
        chain = ProviderChain()
        assert len(chain.provider_list) == 6
        assert chain.provider_list[0].ad == "deepseek"
        assert chain.provider_list[-1].ad == "litellm"

    def test_durum_raporu_yapisi(self):
        """Happy path: durum_raporu dict dondurmeli."""
        chain = ProviderChain()
        rapor = chain.durum_raporu()
        assert "provider_sayisi" in rapor
        assert "providerlar" in rapor
        assert rapor["provider_sayisi"] == 6
        assert len(rapor["providerlar"]) == 6

    def test_zincire_provider_ekle(self):
        """Happy path: zincir sonuna provider eklenebilmeli."""
        chain = ProviderChain()
        chain.ekle("openai", api_key="test-key")
        assert len(chain.provider_list) == 7
        assert chain.provider_list[-1].ad == "openai"

    def test_bos_mesaj_hatali_ama_hata_yakalanir(self):
        """Bos mesajla calistir — API anahtari olmayacagi icin failover biter."""
        chain = ProviderChain()
        sonuc = chain.calistir(messages=[])
        assert isinstance(sonuc, CalistirSonuc)
        assert sonuc.basarili is False
        assert sonuc.hata == "Tum provider'lar basarisiz oldu"
        assert len(sonuc.denenen_providerlar) <= 6

    def test_provider_fabrikasi_bilinmeyen_ad(self):
        """Error case: tanimsiz provider adi ValueError firlatmali."""
        with pytest.raises(ValueError, match="Bilinmeyen provider"):
            _provider_fabrikasi(ad="bilinmeyen_sahte_provider_xyz")


class TestProviderKayitVeSonuc:
    """Veri siniflari yardimcisi."""

    def test_provider_kayit_varsayilan(self):
        kayit = ProviderKayit(ad="test")
        assert kayit.ad == "test"
        assert kayit.model is None

    def test_calistir_sonuc_varsayilan(self):
        sonuc = CalistirSonuc()
        assert sonuc.yanit == ""
        assert sonuc.basarili is False
