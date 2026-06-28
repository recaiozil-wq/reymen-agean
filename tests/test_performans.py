# -*- coding: utf-8 -*-
"""tests/test_performans.py — Performans modulu testleri."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestIterationBudget:
    def test_analiz(self):
        from iteration_budget import IterationBudget
        b = IterationBudget()
        analiz = b.analiz_et("karmasik gorev dosya web kod")
        assert analiz["karmasiklik"] >= 2

    def test_tur_yonetimi(self):
        from iteration_budget import IterationBudget
        b = IterationBudget(max_tur=3)
        b.tur_basla()
        assert b.tur == 1
        b.tur_bitir(basarili=True)

    def test_circuit_breaker(self):
        from iteration_budget import IterationBudget
        b = IterationBudget(max_hata=3)
        for _ in range(3):
            b.tur_basla()
            b.tur_bitir(basarili=False, hata_tipi="genel")
        assert not b.devam_etmeli_mi()


class TestPromptCaching:
    def test_cache_hit(self):
        from prompt_caching import PromptCache
        c = PromptCache(max_boyut=5, ttl_saniye=10)
        c.ekle("test", [{"role": "user", "content": "merhaba"}], "yanit")
        hit = c.al("test", [{"role": "user", "content": "merhaba"}])
        assert hit == "yanit"

    def test_cache_miss(self):
        from prompt_caching import PromptCache
        c = PromptCache(max_boyut=5, ttl_saniye=10)
        miss = c.al("yok", [{"role": "user", "content": "yok"}])
        assert miss is None


class TestRateLimit:
    def test_guard(self):
        from nous_rate_guard import RateGuard
        g = RateGuard(max_per_second=10, max_concurrent=3)
        assert g.izin_ver("test")
        g.istek_basla("test")
        g.istek_bitir("test")
