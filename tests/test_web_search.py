# -*- coding: utf-8 -*-
"""
test_web_search.py — ReYMeN web arama motoru testi.

Tum 7 engine'in:
  - Dogru ad dondurdugunu
  - Bagimlilik kontrollerini dogru yaptigini
  - Calistir metodunun calistigini (gercek API veya hata mesaji)
  - Dispatcher'in engine'leri dogru kaydettigini
  - Auto-detect'in dogru calistigini

Test eder ve sonuclari stdout'a basar.
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

# Proje kokunu PATH'e ekle
PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Engine Birim Testleri
# ═══════════════════════════════════════════════════════════════════════════════

class TestEngineNames(unittest.TestCase):
    """Her engine'in adi dogru mu?"""

    def test_duckduckgo_ad(self):
        from reymen.arac.web_search_engine import DuckDuckGoEngine
        self.assertEqual(DuckDuckGoEngine().ad, "duckduckgo")

    def test_google_ad(self):
        from reymen.arac.web_search_engine import GoogleEngine
        self.assertEqual(GoogleEngine().ad, "google")

    def test_bing_ad(self):
        from reymen.arac.web_search_engine import BingEngine
        self.assertEqual(BingEngine().ad, "bing")

    def test_firecrawl_ad(self):
        from reymen.arac.web_search_engine import FirecrawlEngine
        self.assertEqual(FirecrawlEngine().ad, "firecrawl")

    def test_brave_ad(self):
        from reymen.arac.web_search_engine import BraveSearchEngine
        self.assertEqual(BraveSearchEngine().ad, "brave")

    def test_searxng_ad(self):
        from reymen.arac.web_search_engine import SearXNGEngine
        self.assertEqual(SearXNGEngine().ad, "searxng")

    def test_exa_ad(self):
        from reymen.arac.web_search_engine import ExaEngine
        self.assertEqual(ExaEngine().ad, "exa")


class TestEngineBagimlilikKontrolu(unittest.TestCase):
    """Bagimlilik kontrolleri dogru calisiyor mu?"""

    def setUp(self):
        # Temiz ortam — env var'larini temizle
        for key in ["FIRECRAWL_API_KEY", "FIRECRAWL_KEY", "BRAVE_API_KEY",
                     "SEARXNG_URL", "EXA_API_KEY", "GOOGLE_API_KEY",
                     "GOOGLE_CX", "BING_API_KEY"]:
            os.environ.pop(key, None)

    def test_duckduckgo_her_zaman_hazir(self):
        from reymen.arac.web_search_engine import DuckDuckGoEngine
        eng = DuckDuckGoEngine()
        self.assertTrue(eng.hazir)

    def test_google_hazir_degil(self):
        from reymen.arac.web_search_engine import GoogleEngine
        eng = GoogleEngine()
        self.assertFalse(eng.hazir)

    def test_google_hazir_key_ile(self):
        from reymen.arac.web_search_engine import GoogleEngine
        os.environ["GOOGLE_API_KEY"] = "test-key"
        os.environ["GOOGLE_CX"] = "test-cx"
        eng = GoogleEngine()
        self.assertTrue(eng.hazir)

    def test_bing_hazir_degil(self):
        from reymen.arac.web_search_engine import BingEngine
        eng = BingEngine()
        self.assertFalse(eng.hazir)

    def test_firecrawl_hazir_degil(self):
        from reymen.arac.web_search_engine import FirecrawlEngine
        eng = FirecrawlEngine()
        self.assertFalse(eng.hazir)

    def test_brave_hazir_degil(self):
        from reymen.arac.web_search_engine import BraveSearchEngine
        eng = BraveSearchEngine()
        self.assertFalse(eng.hazir)

    def test_searxng_hazir_degil(self):
        from reymen.arac.web_search_engine import SearXNGEngine
        eng = SearXNGEngine()
        self.assertFalse(eng.hazir)

    def test_exa_hazir_degil(self):
        from reymen.arac.web_search_engine import ExaEngine
        eng = ExaEngine()
        self.assertFalse(eng.hazir)

    def test_brave_hazir_degilse_hata_mesaji(self):
        from reymen.arac.web_search_engine import BraveSearchEngine
        eng = BraveSearchEngine()
        hata = eng.hazir_degilse_hata()
        self.assertIsNotNone(hata)
        assert hata is not None  # type guard
        self.assertIn("BRAVE_API_KEY", hata)

    def test_searxng_hazir_degilse_hata_mesaji(self):
        from reymen.arac.web_search_engine import SearXNGEngine
        eng = SearXNGEngine()
        hata = eng.hazir_degilse_hata()
        self.assertIsNotNone(hata)
        assert hata is not None  # type guard
        self.assertIn("SEARXNG_URL", hata)


class TestEngineCalistir(unittest.TestCase):
    """Engine'lerin calistir metodu hata firlatmadan calisiyor mu?"""

    def setUp(self):
        for key in ["FIRECRAWL_API_KEY", "FIRECRAWL_KEY", "BRAVE_API_KEY",
                     "SEARXNG_URL", "EXA_API_KEY", "GOOGLE_API_KEY",
                     "GOOGLE_CX", "BING_API_KEY"]:
            os.environ.pop(key, None)

    def test_duckduckgo_calistir(self):
        from reymen.arac.web_search_engine import DuckDuckGoEngine
        eng = DuckDuckGoEngine()
        sonuc = eng.calistir("python asyncio", max_sonuc=3)
        self.assertIsInstance(sonuc, str)
        self.assertGreater(len(sonuc), 5)
        print(f"\n[DuckDuckGo] {len(sonuc)} karakter donduruldu")

    def test_google_stub(self):
        from reymen.arac.web_search_engine import GoogleEngine
        eng = GoogleEngine()
        try:
            sonuc = eng.calistir("test", max_sonuc=3)
        except NotImplementedError as e:
            sonuc = str(e)
        self.assertIsInstance(sonuc, str)

    def test_bing_stub(self):
        from reymen.arac.web_search_engine import BingEngine
        eng = BingEngine()
        try:
            sonuc = eng.calistir("test", max_sonuc=3)
        except NotImplementedError as e:
            sonuc = str(e)
        self.assertIsInstance(sonuc, str)

    def test_firecrawl_key_yok(self):
        from reymen.arac.web_search_engine import FirecrawlEngine
        eng = FirecrawlEngine()
        sonuc = eng.calistir("test", max_sonuc=3)
        self.assertIn("FIRECRAWL", sonuc)

    def test_brave_key_yok(self):
        from reymen.arac.web_search_engine import BraveSearchEngine
        eng = BraveSearchEngine()
        sonuc = eng.calistir("test", max_sonuc=3)
        self.assertIn("BRAVE", sonuc)

    def test_searxng_public_instance_fallback(self):
        from reymen.arac.web_search_engine import SearXNGEngine
        eng = SearXNGEngine()
        sonuc = eng.calistir("python", max_sonuc=2)
        self.assertIsInstance(sonuc, str)
        print(f"\n[SearXNG] {sonuc[:80]}...")

    def test_exa_key_yok(self):
        from reymen.arac.web_search_engine import ExaEngine
        eng = ExaEngine()
        sonuc = eng.calistir("test", max_sonuc=3)
        self.assertIn("EXA", sonuc)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SearchDispatcher Testleri
# ═══════════════════════════════════════════════════════════════════════════════

class TestSearchDispatcher(unittest.TestCase):
    """SearchDispatcher testleri."""

    def setUp(self):
        for key in ["FIRECRAWL_API_KEY", "FIRECRAWL_KEY", "BRAVE_API_KEY",
                     "SEARXNG_URL", "EXA_API_KEY", "GOOGLE_API_KEY",
                     "GOOGLE_CX", "BING_API_KEY"]:
            os.environ.pop(key, None)

    def test_kaydet_ve_sec(self):
        from reymen.arac.web_search_engine import SearchDispatcher, DuckDuckGoEngine
        d = SearchDispatcher()
        d.kaydet(DuckDuckGoEngine())
        self.assertIsNotNone(d.sec("duckduckgo"))
        self.assertIsNotNone(d.varsayilan)
        self.assertEqual(d.varsayilan_ad, "duckduckgo")

    def test_tum_engine_kaydet(self):
        from reymen.arac.web_search_engine import (
            SearchDispatcher, DuckDuckGoEngine, GoogleEngine,
            BingEngine, FirecrawlEngine, BraveSearchEngine,
            SearXNGEngine, ExaEngine,
        )
        d = SearchDispatcher()
        for e in [DuckDuckGoEngine(), GoogleEngine(), BingEngine(),
                   FirecrawlEngine(), BraveSearchEngine(),
                   SearXNGEngine(), ExaEngine()]:
            d.kaydet(e)
        liste = d.engine_listele()
        self.assertIn("duckduckgo", liste)
        self.assertIn("google", liste)
        self.assertIn("bing", liste)
        self.assertIn("firecrawl", liste)
        self.assertIn("brave", liste)
        self.assertIn("searxng", liste)
        self.assertIn("exa", liste)

    def test_ara_auto_detect(self):
        from reymen.arac.web_search_engine import SearchDispatcher, DuckDuckGoEngine
        d = SearchDispatcher()
        d.kaydet(DuckDuckGoEngine())
        sonuc = d.ara("test", engine="auto", max_sonuc=2)
        self.assertIsInstance(sonuc, str)
        self.assertGreater(len(sonuc), 5)

    def test_ara_bilinmeyen_engine(self):
        from reymen.arac.web_search_engine import SearchDispatcher
        d = SearchDispatcher()
        sonuc = d.ara("test", engine="olmayan_engine", max_sonuc=2)
        self.assertIn("bulunamadi", sonuc.lower())

    def test_config_backend_secimi(self):
        from reymen.arac.web_search_engine import SearchDispatcher, DuckDuckGoEngine
        config = {"web": {"backend": "duckduckgo"}}
        d = SearchDispatcher(config=config)
        d.kaydet(DuckDuckGoEngine())
        self.assertEqual(d.varsayilan_ad, "duckduckgo")

    def test_env_backend_secimi(self):
        from reymen.arac.web_search_engine import SearchDispatcher, DuckDuckGoEngine
        os.environ["WEB_SEARCH_BACKEND"] = "duckduckgo"
        d = SearchDispatcher()
        d.kaydet(DuckDuckGoEngine())
        self.assertEqual(d.varsayilan_ad, "duckduckgo")
        del os.environ["WEB_SEARCH_BACKEND"]

    def test_sonuc_formatla_bos(self):
        from reymen.arac.web_search_engine import WebSearchEngine
        sonuc = WebSearchEngine._sonuc_formatla([], "Test")
        self.assertEqual(sonuc, "")

    def test_sonuc_formatla_dolu(self):
        from reymen.arac.web_search_engine import WebSearchEngine
        results = [
            {"title": "Baslik 1", "url": "https://ornek.com", "body": "Icerik 1"},
            {"title": "Baslik 2", "url": "https://ornek2.com", "body": "Icerik 2"},
        ]
        sonuc = WebSearchEngine._sonuc_formatla(results, "Test")
        self.assertIn("Baslik 1", sonuc)
        self.assertIn("Baslik 2", sonuc)
        self.assertIn("https://ornek.com", sonuc)

    def test_sonuc_formatla_farkli_key(self):
        from reymen.arac.web_search_engine import WebSearchEngine
        results = [
            {"baslik": "Turkce Baslik", "href": "https://ornek.com", "ozet": "Turkce Ozet"},
        ]
        sonuc = WebSearchEngine._sonuc_formatla(results, "Test")
        self.assertIn("Turkce Baslik", sonuc)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Tool Fonksiyon Testleri
# ═══════════════════════════════════════════════════════════════════════════════

class TestToolFunctions(unittest.TestCase):
    """web_arama ve web_search_engine_listele fonksiyon testleri."""

    def setUp(self):
        from reymen.arac.web_search_engine import reset_registry
        reset_registry()
        for key in ["FIRECRAWL_API_KEY", "FIRECRAWL_KEY", "BRAVE_API_KEY",
                     "SEARXNG_URL", "EXA_API_KEY", "GOOGLE_API_KEY",
                     "GOOGLE_CX", "BING_API_KEY"]:
            os.environ.pop(key, None)

    def test_web_arama_duckduckgo(self):
        from reymen.arac.web_search_engine import web_arama
        sonuc = web_arama("test sorgu", backend="duckduckgo", max_sonuc=2)
        self.assertIsInstance(sonuc, str)
        self.assertGreater(len(sonuc), 5)
        print(f"\n[WEB_ARAMA duckduckgo] {sonuc[:60]}...")

    def test_web_arama_auto(self):
        from reymen.arac.web_search_engine import web_arama
        sonuc = web_arama("test", backend="auto", max_sonuc=2)
        self.assertIsInstance(sonuc, str)

    def test_web_search_engine_listele(self):
        from reymen.arac.web_search_engine import web_search_engine_listele
        liste = web_search_engine_listele()
        self.assertIsInstance(liste, str)
        self.assertIn("duckduckgo", liste)
        print(f"\n[ENGINE LISTELE]\n{liste}")

    def test_web_arama_kaydet_motor(self):
        from reymen.arac.web_search_engine import motor_kaydet
        class MockMotor:
            def __init__(self):
                self.tools = {}
            def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
                self.tools[ad] = fonk
        m = MockMotor()
        motor_kaydet(m)
        self.assertIn("WEB_ARAMA", m.tools)
        self.assertIn("WEB_ARAMA_BACKEND_LISTELE", m.tools)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Gerçek Web Araması Testleri (Canlı)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCanliArama(unittest.TestCase):
    """Gerçek API'leri kullanarak canli arama testi."""

    def test_duckduckgo_canli(self):
        from reymen.arac.web_search_engine import DuckDuckGoEngine
        eng = DuckDuckGoEngine()
        sonuc = eng.calistir("ReYMeN AI agent", max_sonuc=3)
        print(f"\n{'='*60}")
        print("[CANLI] DuckDuckGo → 'ReYMeN AI agent'")
        print(f"{'='*60}")
        print(sonuc)
        self.assertIsInstance(sonuc, str)
        self.assertGreater(len(sonuc), 10)

    def test_searxng_canli_fallback(self):
        from reymen.arac.web_search_engine import SearXNGEngine
        eng = SearXNGEngine()
        sonuc = eng.calistir("python programming", max_sonuc=2)
        print(f"\n{'='*60}")
        print("[CANLI] SearXNG → public instances")
        print(f"{'='*60}")
        print(sonuc)
        self.assertIsInstance(sonuc, str)

    def test_brave_key_yok_canli(self):
        from reymen.arac.web_search_engine import BraveSearchEngine
        eng = BraveSearchEngine()
        sonuc = eng.calistir("test", max_sonuc=2)
        print(f"\n{'='*60}")
        print("[CANLI] Brave → (API key yok)")
        print(f"{'='*60}")
        print(sonuc)
        self.assertIn("BRAVE", sonuc)


# ═══════════════════════════════════════════════════════════════════════════════
# Ana Calistirici
# ═══════════════════════════════════════════════════════════════════════════════

def engine_durum_raporu():
    """Tum engine'lerin durum raporunu stdout'a bas."""
    from reymen.arac.web_search_engine import _get_registry, reset_registry
    reset_registry()
    reg = _get_registry()
    print("\n" + "=" * 60)
    print("  ReYMeN Web Arama Motoru — Engine Durum Raporu")
    print("=" * 60)
    print(f"\n{reg.engine_listele()}")
    print()
    for ad, eng in sorted(reg._engines.items()):
        durum = "HAZIR" if eng.hazir else "HAZIR DEGIL"
        hata = ""
        if not eng.hazir:
            h = eng.hazir_degilse_hata()
            if h:
                hata = f"\n    -> {h[:100]}..."
        print(f"  [{durum}] {ad}{hata}")
    print("=" * 60)


def canli_arama_demo():
    """Her engine ile canli arama demo."""
    from reymen.arac.web_search_engine import reset_registry, web_arama
    reset_registry()

    engines = [
        ("duckduckgo", "DuckDuckGo (API key gerekmez)"),
        ("google", "Google (stub)"),
        ("bing", "Bing (stub)"),
        ("firecrawl", "Firecrawl (API key gerekli)"),
        ("brave", "Brave (API key gerekli)"),
        ("searxng", "SearXNG (public instance)"),
        ("exa", "Exa (API key gerekli)"),
        ("auto", "Auto-detect"),
    ]

    sorgu = "yapay zeka nedir"
    for backend, aciklama in engines:
        print(f"\n{'─'*50}")
        print(f"  [{backend}] {aciklama}")
        print(f"{'─'*50}")
        sonuc = web_arama(sorgu, backend=backend, max_sonuc=3)
        print(sonuc)


if __name__ == "__main__":
    print("=" * 60)
    print("  ReYMeN Web Arama Motoru Testleri")
    print("  Tarih: 2026-06-30")
    print("=" * 60)

    # 1. Durum raporu
    engine_durum_raporu()

    # 2. Canli demo
    canli_arama_demo()

    # 3. unittest
    print("\n" + "=" * 60)
    print("  Unit Testler")
    print("=" * 60)
    unittest.main(verbosity=2, exit=False)
