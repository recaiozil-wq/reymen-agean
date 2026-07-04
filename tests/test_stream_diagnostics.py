# -*- coding: utf-8 -*-
"""Testler: reymen.cereyan.stream_diagnostics"""

import time
import pytest
from reymen.cereyan.stream_diagnostics import (
    StreamDenemesi,
    StreamSaglikTakibi,
)


class TestStreamDenemesi:
    def test_baslangic_zamani_ayarlanir(self):
        d = StreamDenemesi()
        assert d.baslangic > 0
        assert d.ilk_token_zamani is None
        assert d.bitis is None
        assert d.token_sayisi == 0
        assert d.hata is None

    def test_ilk_token_kaydet(self):
        d = StreamDenemesi()
        d.ilk_token_kaydet()
        assert d.ilk_token_zamani is not None

    def test_ilk_token_kaydet_ikinci_cagri_degismez(self):
        d = StreamDenemesi()
        d.ilk_token_kaydet()
        ilk = d.ilk_token_zamani
        time.sleep(0.01)
        d.ilk_token_kaydet()
        assert d.ilk_token_zamani == ilk

    def test_token_ekle_ilk_token_otomatik_kaydedilir(self):
        d = StreamDenemesi()
        assert d.ilk_token_zamani is None
        d.token_ekle(5)
        assert d.ilk_token_zamani is not None
        assert d.token_sayisi == 5

    def test_token_ekle_birden_fazla(self):
        d = StreamDenemesi()
        d.token_ekle(3)
        d.token_ekle(7)
        assert d.token_sayisi == 10

    def test_bitir_hata_yok(self):
        d = StreamDenemesi()
        d.token_ekle(1)
        d.bitir()
        assert d.bitis is not None
        assert d.hata is None
        assert d.basarili is True

    def test_bitir_hatayla(self):
        d = StreamDenemesi()
        d.bitir(hata="timeout")
        assert d.hata == "timeout"
        assert d.basarili is False

    def test_ilk_token_gecikme_hesabi(self):
        d = StreamDenemesi()
        time.sleep(0.01)
        d.ilk_token_kaydet()
        gecikme = d.ilk_token_gecikme
        assert gecikme is not None
        assert gecikme >= 0.005

    def test_ilk_token_gecikme_none_token_yoksa(self):
        d = StreamDenemesi()
        assert d.ilk_token_gecikme is None

    def test_toplam_sure_artar(self):
        d = StreamDenemesi()
        sure1 = d.toplam_sure
        time.sleep(0.02)
        sure2 = d.toplam_sure
        assert sure2 > sure1

    def test_toplam_sure_sabit_bittikten_sonra(self):
        d = StreamDenemesi()
        d.token_ekle(1)
        d.bitir()
        sure1 = d.toplam_sure
        time.sleep(0.02)
        sure2 = d.toplam_sure
        assert abs(sure1 - sure2) < 0.001

    def test_token_hizi_hesabi(self):
        d = StreamDenemesi()
        d.token_ekle(100)
        time.sleep(0.05)
        d.bitir()
        hiz = d.token_hizi
        assert hiz is not None
        assert hiz > 0

    def test_token_hizi_none_token_yoksa(self):
        d = StreamDenemesi()
        assert d.token_hizi is None

    def test_ozet_dict(self):
        d = StreamDenemesi(provider="deepseek", model="deepseek-chat")
        d.token_ekle(10)
        d.bitir()
        ozet = d.ozet()
        assert ozet["provider"] == "deepseek"
        assert ozet["model"] == "deepseek-chat"
        assert ozet["token_sayisi"] == 10
        assert ozet["basarili"] is True
        assert "toplam_sure_sn" in ozet
        assert "ilk_token_gecikme_sn" in ozet


class TestStreamSaglikTakibi:
    def test_bos_baslangic(self):
        t = StreamSaglikTakibi()
        assert t.toplam_deneme == 0
        assert t.basarili_deneme == 0
        assert t.son_deneme is None

    def test_yeni_deneme_olusturur(self):
        t = StreamSaglikTakibi()
        d = t.yeni_deneme(provider="groq", model="llama-3")
        assert t.toplam_deneme == 1
        assert t.son_deneme is d
        assert d.provider == "groq"
        assert d.model == "llama-3"

    def test_birden_fazla_deneme(self):
        t = StreamSaglikTakibi()
        t.yeni_deneme()
        t.yeni_deneme()
        t.yeni_deneme()
        assert t.toplam_deneme == 3

    def test_ask_mi_ilk_token_yok_uzun_bekleme(self):
        t = StreamSaglikTakibi(max_ilk_token_bekleme=0.01)
        d = t.yeni_deneme()
        time.sleep(0.05)
        assert t.ask_mi(d) is True

    def test_ask_mi_ilk_token_var_kisa_bekleme(self):
        t = StreamSaglikTakibi(max_ilk_token_bekleme=30.0)
        d = t.yeni_deneme()
        d.ilk_token_kaydet()
        assert t.ask_mi(d) is False

    def test_ask_mi_dusuk_token_hizi(self):
        t = StreamSaglikTakibi(min_token_hizi=100.0)  # çok yüksek minimum
        d = t.yeni_deneme()
        d.token_ekle(1)
        time.sleep(0.05)  # hız çok düşük
        assert t.ask_mi(d) is True

    def test_ask_mi_yeterli_hiz(self):
        t = StreamSaglikTakibi(min_token_hizi=0.01)  # çok düşük minimum
        d = t.yeni_deneme()
        d.token_ekle(100)
        assert t.ask_mi(d) is False

    def test_basarili_deneme_sayisi(self):
        t = StreamSaglikTakibi()
        d1 = t.yeni_deneme()
        d1.token_ekle(1)
        d1.bitir()
        d2 = t.yeni_deneme()
        d2.bitir(hata="zaman aşımı")
        assert t.basarili_deneme == 1

    def test_ortalama_ilk_token_none_bos(self):
        t = StreamSaglikTakibi()
        assert t.ortalama_ilk_token() is None

    def test_ortalama_ilk_token_hesabi(self):
        t = StreamSaglikTakibi()
        d1 = t.yeni_deneme()
        d1.ilk_token_kaydet()
        d2 = t.yeni_deneme()
        d2.ilk_token_kaydet()
        ort = t.ortalama_ilk_token()
        assert ort is not None
        assert ort >= 0

    def test_ozet_dict(self):
        t = StreamSaglikTakibi()
        d = t.yeni_deneme(provider="openai")
        d.token_ekle(5)
        d.bitir()
        ozet = t.ozet()
        assert ozet["toplam_deneme"] == 1
        assert ozet["basarili"] == 1
        assert len(ozet["denemeler"]) == 1
        assert ozet["denemeler"][0]["provider"] == "openai"
