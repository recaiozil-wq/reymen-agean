# -*- coding: utf-8 -*-
"""tests/test_akil.py — AI/context modulleri testleri."""

import sys
import json
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from context_engine import ContextEngine
from context_compressor import ContextCompressor
from error_classifier import ErrorClassifier


class TestContextEngine:
    def test_context_engine_olusturma(self):
        """ContextEngine baslatma."""
        ce = ContextEngine(max_token=8000)
        assert ce is not None
        assert ce.max_token == 8000

    def test_baglam_hazirla_bos(self):
        """Bos gecmisle baglam hazirlama."""
        ce = ContextEngine()
        sonuc = ce.baglam_hazirla([], "merhaba")
        assert "ozet" in sonuc
        assert "onemli" in sonuc
        assert "yeni_mesaj" in sonuc
        assert "token_tahmini" in sonuc
        assert sonuc["yeni_mesaj"] == "merhaba"

    def test_baglam_hazirla_onemli(self):
        """Gecmisten onemli bilgi ayiklama."""
        ce = ContextEngine()
        gecmis = [
            {"icerik": "Hedefimiz bir web sitesi kurmak"},
            {"icerik": "Kisitlama: Python kullanilacak"},
        ]
        sonuc = ce.baglam_hazirla(gecmis, "devam")
        assert "hedef" in sonuc["onemli"] or "kisitlama" in sonuc["onemli"]

    def test_token_limit_asti_mi_false(self):
        """Token limiti asilmamissa false donmeli."""
        ce = ContextEngine(max_token=16000)
        assert ce.token_limit_asti_mi([], "kisa mesaj") is False

    def test_token_limit_asti_mi_true(self):
        """Token limiti asilmissa true donmeli."""
        ce = ContextEngine(max_token=10)
        gecmis = [{"icerik": "x" * 100}]
        assert ce.token_limit_asti_mi(gecmis, "y" * 100) is True

    def test_onemli_anahtarlar(self):
        """Onemli anahtar kelimelerin dogru tespiti."""
        ce = ContextEngine()
        onemli = ce._onemli_bilgileri_ayikla(
            [
                {"icerik": "API anahtari ve URL ayarlandi"},
                {"icerik": "Dosya yolu belirlendi"},
            ]
        )
        assert len(onemli) >= 1

    def test_ozetle_kisa_gecmis(self):
        """Kisa gecmis bos ozet donmeli."""
        ce = ContextEngine()
        ozet = ce._ozetle([{"icerik": "test"}])
        assert ozet == ""

    def test_ozetle_uzun_gecmis(self):
        """Uzun gecmis ozetlenmeli."""
        ce = ContextEngine()
        gecmis = [{"icerik": f"mesaj {i}"} for i in range(10)]
        ozet = ce._ozetle(gecmis)
        assert len(ozet) > 0


class TestContextCompressor:
    def test_compressor_olusturma(self):
        """ContextCompressor baslatma."""
        cc = ContextCompressor(max_token=4096)
        assert cc is not None
        assert cc._max_token == 4096

    def test_sikistir_bos(self):
        """Bos gecmis sikistirma."""
        cc = ContextCompressor()
        sikistirilmis = cc.sikistir([])
        assert sikistirilmis == []

    def test_sikistir_basit(self):
        """Basit gecmis sikistirma."""
        cc = ContextCompressor()
        gecmis = [{"rol": "user", "icerik": "merhaba"}]
        sikistirilmis = cc.sikistir(gecmis)
        assert len(sikistirilmis) > 0
        assert any(
            "[OZET]" in m.get("icerik", "")
            for m in sikistirilmis
            if isinstance(m, dict)
        )

    def test_onemli_bilgileri_sakla(self):
        """Onemli bilgi saklama."""
        cc = ContextCompressor()
        cc.onemli_bilgileri_sakla("test_anahtar", "test_deger")
        assert "test_anahtar" in cc._onemli_bilgiler
        assert cc._onemli_bilgiler["test_anahtar"] == "test_deger"

    def test_onemli_bilgi_json_sakla(self):
        """JSON formatinda onemli bilgi saklama."""
        cc = ContextCompressor()
        bilgi = {"sehir": "Istanbul", "ulke": "Turkiye"}
        cc.onemli_bilgileri_sakla("konum", bilgi)
        assert cc._onemli_bilgiler["konum"] == bilgi

    def test_ozet_olustur(self):
        """Ozet olusturma metodu varligi."""
        cc = ContextCompressor()
        ozet = cc.ozet_olustur([{"rol": "user", "icerik": "test icerik"}])
        assert isinstance(ozet, str)

    def test_token_hesapla(self):
        """Token hesaplama."""
        cc = ContextCompressor()
        token = cc._token_hesapla([{"rol": "user", "icerik": "test"}])
        assert isinstance(token, int)
        assert token > 0


class TestErrorClassifier:
    def test_error_classifier_olusturma(self):
        """ErrorClassifier baslatma."""
        ec = ErrorClassifier()
        assert ec is not None
        assert "import" in ec.KATEGORILER
        assert "api" in ec.COZUM_ONERILERI

    def test_siniflandir_import(self):
        """Import hatasi siniflandirmasi."""
        ec = ErrorClassifier()
        sonuc = ec.siniflandir("ImportError: No module named 'requests'")
        assert sonuc["kategori"] == "import"
        assert "cozum" in sonuc

    def test_siniflandir_syntax(self):
        """Syntax hatasi siniflandirmasi."""
        ec = ErrorClassifier()
        sonuc = ec.siniflandir("SyntaxError: invalid syntax on line 10")
        assert sonuc["kategori"] == "syntax"

    def test_siniflandir_dizin(self):
        """Dizin hatasi siniflandirmasi."""
        ec = ErrorClassifier()
        sonuc = ec.siniflandir("FileNotFoundError: dosya bulunamadi")
        assert sonuc["kategori"] == "dizin"

    def test_siniflandir_baglanti(self):
        """Baglanti hatasi siniflandirmasi."""
        ec = ErrorClassifier()
        sonuc = ec.siniflandir("ConnectionError: Baglanti reddedildi")
        assert sonuc["kategori"] == "baglanti"

    def test_siniflandir_api(self):
        """API hatasi siniflandirmasi."""
        ec = ErrorClassifier()
        sonuc = ec.siniflandir("HTTP 401: Unauthorized - API key gecersiz")
        assert sonuc["kategori"] == "api"

    def test_siniflandir_bilinmeyen(self):
        """Bilinmeyen hata siniflandirmasi."""
        ec = ErrorClassifier()
        sonuc = ec.siniflandir("Beklenmedik bir hata olustu")
        assert sonuc["kategori"] == "diger"

    def test_cozum_onerisi(self):
        """Cozum onerisi dogrulama."""
        ec = ErrorClassifier()
        sonuc = ec.siniflandir("ImportError: No module named 'pandas'")
        assert "pip install" in sonuc["cozum"]

    def test_traceback_analiz(self):
        """Traceback analizi."""
        ec = ErrorClassifier()
        tb = """Traceback (most recent call last):
  File "test.py", line 5, in <module>
    import nonexistent_module
ModuleNotFoundError: No module named 'nonexistent_module'"""
        sonuc = ec.siniflandir(tb)
        assert sonuc["kategori"] in ("import", "diger")

    def test_exception_nesnesi(self):
        """Exception nesnesi ile siniflandirma."""
        ec = ErrorClassifier()
        try:
            raise ValueError("gecersiz deger")
        except ValueError as e:
            sonuc = ec.siniflandir(e)
            assert sonuc["kategori"] in ("tip", "diger")
