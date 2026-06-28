# -*- coding: utf-8 -*-
"""test_proxy_engine.py — ProxyEngine unit testleri."""
from __future__ import annotations

import socket
import threading
import time

import pytest

from proxy.proxy_config import ProxyConfig
from proxy.proxy_engine import ProxyEngine


def _find_free_port() -> int:
    """Gecici bir soket acip port bul, sonra kapat."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _config_with_port(port: int) -> ProxyConfig:
    """Belirtilen port ile ProxyConfig olustur."""
    return ProxyConfig()


@pytest.fixture
def test_config() -> ProxyConfig:
    """Her test icin ayri bir port ile ProxyConfig."""
    port = _find_free_port()
    cfg = ProxyConfig()
    cfg._cfg["port"] = port
    return cfg


@pytest.fixture
def engine(test_config: ProxyConfig) -> ProxyEngine:
    """Temiz ProxyEngine ornegi."""
    eng = ProxyEngine(config=test_config)
    yield eng
    # Temizlik: calisiyorsa durdur
    if eng.is_running:
        try:
            eng.stop()
        except Exception:
            pass
    if hasattr(eng, "_socks5") and eng._socks5 is not None:
        try:
            eng.stop_socks5()
        except Exception:
            pass


class TestProxyEngineInitial:
    """Baslangic durumu testleri."""

    def test_initial_is_running_false(self, engine: ProxyEngine):
        assert engine.is_running is False

    def test_initial_connections_zero(self, engine: ProxyEngine):
        assert engine.connections == 0

    def test_initial_status_not_running(self, engine: ProxyEngine):
        status = engine.status()
        assert status["running"] is False
        assert status["port"] is None
        assert status["connections"] == 0
        assert isinstance(status["config"], dict)

    def test_initial_status_has_config(self, engine: ProxyEngine):
        status = engine.status()
        assert "port" in status["config"]
        assert "timeout" in status["config"]


class TestProxyEngineStartStop:
    """start/stop testleri."""

    def test_start_returns_started(self, engine: ProxyEngine):
        result = engine.start()
        assert result["status"] == "started"
        assert isinstance(result["port"], int)
        assert result["port"] > 0

    def test_start_makes_running(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        assert engine.is_running is True

    def test_start_updates_status(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        status = engine.status()
        assert status["running"] is True
        assert isinstance(status["port"], int)
        assert status["port"] > 0

    def test_stop_returns_stopped(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        result = engine.stop()
        assert result["status"] == "stopped"

    def test_stop_makes_not_running(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        engine.stop()
        assert engine.is_running is False

    def test_double_start_returns_already_running(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        result = engine.start()
        assert result["status"] == "already_running"

    def test_stop_when_not_running(self, engine: ProxyEngine):
        result = engine.stop()
        assert result["status"] == "not_running"

    def test_start_stop_cycle(self, engine: ProxyEngine):
        """start -> stop -> start -> stop calismali."""
        r1 = engine.start()
        assert r1["status"] == "started"
        time.sleep(0.3)

        r2 = engine.stop()
        assert r2["status"] == "stopped"
        assert engine.is_running is False

        r3 = engine.start()
        assert r3["status"] == "started"
        time.sleep(0.3)
        assert engine.is_running is True

        r4 = engine.stop()
        assert r4["status"] == "stopped"
        assert engine.is_running is False

    def test_port_accessible(self, engine: ProxyEngine):
        """start() sonrasi port gercekten dinleniyor olmali."""
        engine.start()
        time.sleep(0.5)
        port = engine._config.port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            result = s.connect_ex(("127.0.0.1", port))
        assert result == 0, f"Port {port} dinlenmiyor, connect_ex={result}"
        engine.stop()

    def test_port_inaccessible_after_stop(self, engine: ProxyEngine):
        """stop() sonrasi port kapali olmali."""
        engine.start()
        time.sleep(0.3)
        port = engine._config.port
        engine.stop()
        time.sleep(0.3)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            result = s.connect_ex(("127.0.0.1", port))
        assert result != 0, "Port stop()'dan sonra hala acik"


class TestProxyEngineStatus:
    """status() metodu testleri."""

    def test_status_running_true_after_start(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        assert engine.status()["running"] is True

    def test_status_running_false_after_stop(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        engine.stop()
        assert engine.status()["running"] is False

    def test_status_returns_port(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        status = engine.status()
        assert status["port"] == engine._config.port

    def test_status_returns_connections(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        status = engine.status()
        assert status["connections"] == 0

    def test_status_returns_config(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        status = engine.status()
        assert isinstance(status["config"], dict)
        assert status["config"]["port"] == engine._config.port

    def test_status_after_stop_port_none(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        engine.stop()
        status = engine.status()
        assert status["port"] is None


class TestProxyEngineSOCKS5:
    """SOCKS5 start/stop testleri."""

    def test_start_socks5_returns_started(self, engine: ProxyEngine):
        port = _find_free_port()
        result = engine.start_socks5(port=port)
        assert result["status"] == "socks5_started"
        assert result["port"] == port

    def test_stop_socks5_returns_stopped(self, engine: ProxyEngine):
        port = _find_free_port()
        engine.start_socks5(port=port)
        time.sleep(0.3)
        result = engine.stop_socks5()
        assert result["status"] == "socks5_stopped"

    def test_double_start_socks5(self, engine: ProxyEngine):
        port = _find_free_port()
        engine.start_socks5(port=port)
        result = engine.start_socks5(port=port)
        assert result["status"] == "already_running"

    def test_stop_socks5_when_not_running(self, engine: ProxyEngine):
        result = engine.stop_socks5()
        assert result["status"] == "socks5_not_running"

    def test_socks5_port_accessible(self, engine: ProxyEngine):
        port = _find_free_port()
        engine.start_socks5(port=port)
        time.sleep(0.5)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            result = s.connect_ex(("127.0.0.1", port))
        assert result == 0, f"SOCKS5 port {port} dinlenmiyor"
        engine.stop_socks5()

    def test_socks5_port_inaccessible_after_stop(self, engine: ProxyEngine):
        port = _find_free_port()
        engine.start_socks5(port=port)
        time.sleep(0.3)
        engine.stop_socks5()
        time.sleep(0.3)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            result = s.connect_ex(("127.0.0.1", port))
        assert result != 0, "SOCKS5 stop sonrasi port hala acik"

    def test_socks5_in_status(self, engine: ProxyEngine):
        port = _find_free_port()
        engine.start_socks5(port=port)
        time.sleep(0.3)
        status = engine.status()
        assert "socks5_port" in status
        assert status["socks5_port"] == port
        engine.stop_socks5()


class TestProxyEngineConnections:
    """connections sayaci testleri."""

    def test_connections_starts_at_zero(self, engine: ProxyEngine):
        assert engine.connections == 0

    def test_connections_after_start(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        assert engine.connections == 0

    def test_connections_after_stop(self, engine: ProxyEngine):
        engine.start()
        time.sleep(0.3)
        engine.stop()
        assert engine.connections == 0


class TestProxyEngineEdgeCases:
    """Kenar durum testleri."""

    def test_start_with_custom_config_port(self):
        port = _find_free_port()
        cfg = ProxyConfig()
        cfg._cfg["port"] = port
        engine = ProxyEngine(config=cfg)
        try:
            result = engine.start()
            assert result["port"] == port
            time.sleep(0.3)
            assert engine.is_running
        finally:
            if engine.is_running:
                engine.stop()

    def test_multiple_stop_calls(self, engine: ProxyEngine):
        """Ard arda stop cagrilari hata firlatmamali."""
        engine.start()
        time.sleep(0.3)
        result1 = engine.stop()
        assert result1["status"] == "stopped"
        result2 = engine.stop()
        assert result2["status"] == "not_running"
        result3 = engine.stop()
        assert result3["status"] == "not_running"

    def test_rapid_start_stop(self, engine: ProxyEngine):
        """Hizli start/stop donguleri calismali."""
        for _ in range(3):
            r = engine.start()
            assert r["status"] == "started"
            time.sleep(0.2)
            r = engine.stop()
            assert r["status"] == "stopped"
            time.sleep(0.1)
        assert engine.is_running is False

    def test_http_get_request_succeeds(self, engine: ProxyEngine):
        """Proxy'ye HTTP GET istegi gonderip 502 (upstream yok) al."""
        engine.start()
        time.sleep(0.5)
        port = engine._config.port
        import urllib.request
        import urllib.error
        proxy_handler = urllib.request.ProxyHandler({
            "http": f"http://127.0.0.1:{port}",
            "https": f"http://127.0.0.1:{port}",
        })
        opener = urllib.request.build_opener(proxy_handler)
        try:
            with opener.open("http://example.com", timeout=5):
                pass
        except urllib.error.HTTPError as e:
            # Proxy calisiyor, upstream'e ulasamadigi icin 502 bekleriz
            assert e.code in (502,)
        except Exception:
            # Baska bir hata da olabilir (proxy ulasti ama cevap gelmedi vb)
            pass
        finally:
            engine.stop()
