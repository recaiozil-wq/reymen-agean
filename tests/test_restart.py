# -*- coding: utf-8 -*-
"""tests/test_restart.py — Gateway restart yöneticisi birim testleri."""
import sys
import time
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from gateway.restart import (
    GATEWAY_SERVICE_RESTART_EXIT_CODE,
    DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT,
    parse_restart_drain_timeout,
    platform_kaydet, platform_listele, platform_kaldir,
    send_restart_signal, restart_platform, restart_all,
    durum_raporu,
    sinyal_yakalama_kur, sinyal_yakalama_kaldir,
)


class TestRestartConstants:
    def test_exit_code(self):
        assert GATEWAY_SERVICE_RESTART_EXIT_CODE == 75

    def test_drain_timeout_default(self):
        assert isinstance(DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT, float)
        assert DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT > 0

    def test_parse_restart_drain_timeout_valid(self):
        assert parse_restart_drain_timeout("15.0") == 15.0

    def test_parse_restart_drain_timeout_invalid(self):
        assert parse_restart_drain_timeout(None) == DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT

    def test_parse_restart_drain_timeout_empty(self):
        assert parse_restart_drain_timeout("") == DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT

    def test_parse_restart_drain_timeout_negative(self):
        assert parse_restart_drain_timeout("-5") == 0.0


class TestRestartManager:
    def _make_fns(self):
        self._baslat_called = False
        self._durdur_called = False
        def baslat():
            self._baslat_called = True
        def durdur():
            self._durdur_called = True
        return baslat, durdur

    def test_platform_kaydet(self):
        baslat, durdur = self._make_fns()
        platform_kaydet("test_p", baslat, durdur)
        assert "test_p" in platform_listele()
        # cleanup
        platform_kaldir("test_p")

    def test_platform_kaydet_with_kontrol(self):
        def kontrol(): return "saglikli"
        platform_kaydet("test_k", lambda: None, lambda: None, kontrol)
        assert "test_k" in platform_listele()
        platform_kaldir("test_k")

    def test_platform_kaldir(self):
        platform_kaydet("tmp_p", lambda: None, lambda: None)
        assert platform_kaldir("tmp_p") is True
        assert platform_kaldir("tmp_p") is False  # zaten yok

    def test_send_restart_signal(self):
        def noop(): pass
        platform_kaydet("sig_test", noop, noop)
        assert send_restart_signal("sig_test", sebep="test") is True
        platform_kaldir("sig_test")

    def test_send_restart_signal_all(self):
        def noop(): pass
        platform_kaydet("sig_a", noop, noop)
        platform_kaydet("sig_b", noop, noop)
        assert send_restart_signal(sebep="test") is True
        platform_kaldir("sig_a")
        platform_kaldir("sig_b")

    def test_send_restart_signal_nonexistent(self):
        assert send_restart_signal("yok_platform") is False

    def test_restart_platform(self):
        self._bc = self._dc = False
        def b(): self._bc = True
        def d(): self._dc = True
        platform_kaydet("restart_test", b, d)
        assert restart_platform("restart_test", bekleme=0.05) is True
        assert self._dc is True
        assert self._bc is True
        platform_kaldir("restart_test")

    def test_restart_platform_not_registered(self):
        assert restart_platform("bulunamadi") is False

    def test_restart_all(self):
        results = {}
        def make_fns(name):
            def b(): pass
            def d(): pass
            return b, d
        platform_kaydet("all_a", *make_fns("a"))
        platform_kaydet("all_b", *make_fns("b"))
        results = restart_all(bekleme=0.05)
        assert results.get("all_a") is True
        assert results.get("all_b") is True
        platform_kaldir("all_a")
        platform_kaldir("all_b")

    def test_durum_raporu(self):
        def noop(): pass
        platform_kaydet("durum_test", noop, noop)
        rapor = durum_raporu()
        assert "durum_test" in rapor
        assert rapor["durum_test"]["durum"] is not None
        platform_kaldir("durum_test")

    def test_restart_platform_with_async_fns(self):
        async def async_baslat(): pass
        async def async_durdur(): pass
        platform_kaydet("async_p", async_baslat, async_durdur)
        # should handle async funcs gracefully
        result = restart_platform("async_p", bekleme=0.05)
        assert result is True
        platform_kaldir("async_p")


class TestSignalHandling:
    def test_sinyal_yakalama_kur_kaldir(self):
        # Should not raise
        sinyal_yakalama_kur()
        sinyal_yakalama_kaldir()
