# -*- coding: utf-8 -*-
"""test_iteration_budget.py — IterationBudget kapsamli testleri.

Thread-safe iterasyon butcesi: consume, refund, reset, geriye uyumlu API.
"""
import threading
import pytest
from reymen.cereyan.iteration_budget import IterationBudget


class TestConstructor:
    def test_default_budget(self):
        b = IterationBudget()
        assert b.max_total == 90
        assert b.used == 0
        assert b.remaining == 90

    def test_custom_max_total(self):
        b = IterationBudget(max_total=10)
        assert b.max_total == 10
        assert b.remaining == 10

    def test_legacy_max_tur(self):
        b = IterationBudget(max_tur=25)
        assert b.max_total == 25
        assert b.remaining == 25

    def test_max_total_takes_precedence(self):
        b = IterationBudget(max_total=50, max_tur=10)
        assert b.max_total == 50

    def test_both_none_defaults_to_90(self):
        b = IterationBudget(max_total=None, max_tur=None)
        assert b.max_total == 90


class TestConsumeRefund:
    def test_consume_once(self):
        b = IterationBudget(max_total=5)
        assert b.consume() is True
        assert b.used == 1
        assert b.remaining == 4

    def test_consume_until_exhausted(self):
        b = IterationBudget(max_total=3)
        assert b.consume() is True
        assert b.consume() is True
        assert b.consume() is True
        assert b.consume() is False
        assert b.used == 3
        assert b.remaining == 0

    def test_refund_decrements(self):
        b = IterationBudget(max_total=5)
        b.consume()
        b.consume()
        b.refund()
        assert b.used == 1
        assert b.remaining == 4

    def test_refund_at_zero_no_negative(self):
        b = IterationBudget(max_total=5)
        b.refund()
        assert b.used == 0
        assert b.remaining == 5

    def test_refund_after_exhaustion(self):
        b = IterationBudget(max_total=2)
        b.consume()
        b.consume()
        assert b.remaining == 0
        b.refund()
        assert b.remaining == 1
        assert b.consume() is True

    def test_reset(self):
        b = IterationBudget(max_total=10)
        for _ in range(10):
            b.consume()
        assert b.remaining == 0
        b.reset()
        assert b.used == 0
        assert b.remaining == 10


class TestProperties:
    def test_used_starts_zero(self):
        b = IterationBudget(max_total=5)
        assert b.used == 0

    def test_remaining_never_negative(self):
        b = IterationBudget(max_total=1)
        b.consume()
        b.consume()
        assert b.remaining >= 0

    def test_repr(self):
        b = IterationBudget(max_total=10)
        b.consume()
        r = repr(b)
        assert "1/10" in r


class TestLegacyAPI:
    def test_tur_property(self):
        b = IterationBudget(max_total=10)
        b.consume()
        b.consume()
        assert b.tur == 2

    def test_max_tur_property(self):
        b = IterationBudget(max_total=15)
        assert b.max_tur == 15

    def test_tur_basla(self):
        b = IterationBudget(max_total=5)
        b.tur_basla()
        assert b.used == 1

    def test_tur_bitir_returns_remaining(self):
        b = IterationBudget(max_total=5)
        assert b.tur_bitir() is True
        for _ in range(5):
            b.consume()
        assert b.tur_bitir() is False

    def test_devam_etmeli_mi(self):
        b = IterationBudget(max_total=2)
        assert b.devam_etmeli_mi() is True
        b.consume()
        b.consume()
        assert b.devam_etmeli_mi() is False

    def test_durum_raporu(self):
        b = IterationBudget(max_total=10)
        b.consume()
        rapor = b.durum_raporu()
        assert "1/10" in rapor

    def test_gorev_tamamla_resets(self):
        b = IterationBudget(max_total=5)
        b.consume()
        b.consume()
        b.gorev_tamamla()
        assert b.used == 0

    def test_gorev_tamami_alias(self):
        b = IterationBudget(max_total=5)
        b.consume()
        b.gorev_tamami()
        assert b.used == 0

    def test_eylem_kaydet_noop(self):
        b = IterationBudget()
        b.eylem_kaydet("test eylem")
        assert b.used == 0

    def test_ozet_dict(self):
        b = IterationBudget(max_total=20)
        b.consume()
        d = b.ozet_dict()
        assert d == {"tur": 1, "max_tur": 20}


class TestAnalizEt:
    def test_basit_gorev(self):
        b = IterationBudget()
        r = b.analiz_et("dosya oku")
        assert r["karmasiklik"] >= 1

    def test_toplu_gorev_karmasiklik_5(self):
        b = IterationBudget()
        r = b.analiz_et("hepsini kontrol et")
        assert r["karmasiklik"] == 5

    def test_toplu_sadece_karmasiklik_4(self):
        b = IterationBudget()
        r = b.analiz_et("tum dosyalar")
        assert r["karmasiklik"] == 4

    def test_cok_adimli_artis(self):
        b = IterationBudget()
        r1 = b.analiz_et("dosya oku")
        r2 = b.analiz_et("dosya oku ve yaz")
        assert r2["karmasiklik"] >= r1["karmasiklik"]

    def test_karmasiklik_max_5(self):
        b = IterationBudget()
        r = b.analiz_et("hepsini kontrol et ve duzelt ve tara ve sil ve guncelle")
        assert r["karmasiklik"] == 5

    def test_karmasiklik_min_1(self):
        b = IterationBudget()
        r = b.analiz_et("selam")
        assert r["karmasiklik"] == 1


class TestThreadSafety:
    def test_concurrent_consume(self):
        b = IterationBudget(max_total=100)
        results = []

        def worker():
            for _ in range(10):
                r = b.consume()
                results.append(r)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 100
        assert b.used <= 100

    def test_concurrent_refund(self):
        b = IterationBudget(max_total=50)
        for _ in range(20):
            b.consume()

        def refund_worker():
            for _ in range(10):
                b.refund()

        threads = [threading.Thread(target=refund_worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert b.used >= 0


class TestEdgeCases:
    def test_zero_budget(self):
        b = IterationBudget(max_total=0)
        assert b.consume() is False
        assert b.remaining == 0

    def test_single_budget(self):
        b = IterationBudget(max_total=1)
        assert b.consume() is True
        assert b.consume() is False
        assert b.remaining == 0

    def test_large_budget(self):
        b = IterationBudget(max_total=10000)
        for _ in range(10000):
            assert b.consume() is True
        assert b.consume() is False
        assert b.remaining == 0
