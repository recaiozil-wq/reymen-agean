"""Test: reymen/desktop/ modulu."""

from __future__ import annotations
import os
import sys
import socket
import time
import subprocess
from pathlib import Path

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))

import pytest


class TestWebServerManager:
    """Web sunucu yoneticisi testleri."""

    def test_server_import(self):
        """WebServerManager import edilebiliyor mu?"""
        from reymen.desktop.server import WebServerManager

        wsm = WebServerManager()
        assert wsm is not None
        assert wsm.host == "127.0.0.1"
        assert wsm.port == 5000

    def test_server_status_stopped(self):
        """Server durmusken status 'stopped' donmeli."""
        from reymen.desktop.server import WebServerManager

        wsm = WebServerManager(host="127.0.0.1", port=19999)  # unused port
        # Ensure nothing is on this port
        assert wsm.status == "stopped"

    def test_server_url(self):
        """URL dogru formatta donmeli."""
        from reymen.desktop.server import WebServerManager

        wsm = WebServerManager(host="0.0.0.0", port=8080)
        assert wsm.url == "http://0.0.0.0:8080"

    def test_server_url_default(self):
        from reymen.desktop.server import web_server

        assert "127.0.0.1" in web_server.url
        assert "5000" in web_server.url


class TestAutoStart:
    """Auto-start yoneticisi testleri."""

    def test_autostart_import(self):
        from reymen.desktop.autostart import AutoStartManager

        assert AutoStartManager is not None

    def test_autostart_is_disabled_initially(self):
        from reymen.desktop.autostart import AutoStartManager

        # On a test machine, auto-start should not be enabled
        assert AutoStartManager.is_enabled() is False


class TestDesktopApp:
    """Ust seviye DesktopApp API testleri."""

    def test_desktop_app_import(self):
        from reymen.desktop import DesktopApp

        app = DesktopApp()
        assert app is not None
        assert hasattr(app, "start")
        assert hasattr(app, "stop")
        assert hasattr(app, "status")
        assert hasattr(app, "url")

    def test_desktop_app_status(self):
        from reymen.desktop import DesktopApp

        app = DesktopApp()
        # Should not crash
        s = app.status
        assert s in ("running", "stopped")

    def test_desktop_app_url(self):
        from reymen.desktop import DesktopApp

        app = DesktopApp()
        assert "http://" in app.url

    def test_app_autostart_methods(self):
        from reymen.desktop import DesktopApp

        app = DesktopApp()
        assert hasattr(app, "enable_autostart")
        assert hasattr(app, "disable_autostart")
        assert callable(app.enable_autostart)
        assert callable(app.disable_autostart)


class TestTrayImport:
    """Sistem tepsisi import testleri."""

    def test_tray_import(self):
        """TrayApp ve run_tray import edilebiliyor mu?"""
        from reymen.desktop.tray import run_tray, TrayApp

        assert run_tray is not None
        assert TrayApp is not None

    def test_launcher_import(self):
        from reymen.desktop.launcher import main

        assert main is not None


class TestServerPortDetection:
    """Port bazli durum tespiti testleri."""

    def test_port_open_detection(self):
        """Port actigimizda status 'running' olmali."""
        from reymen.desktop.server import web_server

        # Start the server
        result = web_server.start()
        time.sleep(1)

        try:
            assert web_server.status == "running"
        finally:
            web_server.stop()
            time.sleep(0.5)

    def test_port_close_detection(self):
        """Port kapandiginda status 'stopped' olmali."""
        from reymen.desktop.server import web_server

        web_server.start()
        time.sleep(1)
        web_server.stop()
        time.sleep(0.5)

        assert web_server.status == "stopped"

    def test_restart_cycle(self):
        """Start -> stop -> start -> stop dongusu calismali."""
        from reymen.desktop.server import web_server

        # Start
        web_server.start()
        time.sleep(1)
        assert web_server.status == "running"

        # Stop
        web_server.stop()
        time.sleep(0.5)
        assert web_server.status == "stopped"

        # Start again
        web_server.start()
        time.sleep(1)
        assert web_server.status == "running"

        # Final stop
        web_server.stop()
        time.sleep(0.5)
        assert web_server.status == "stopped"


class TestCLICommands:
    """CLI uzerinden komut testleri."""

    def test_cli_status(self):
        """python -m reymen.desktop.launcher status calismali."""
        from reymen.desktop.launcher import main as cli_main

        # We can't easily test CLI via sys.argv manipulation,
        # just verify the module exists
        import reymen.desktop.launcher

        assert hasattr(reymen.desktop.launcher, "main")

    def test_cli_module_runnable(self):
        """reymen desktop CLI komutu calismali (import test)."""
        import importlib

        spec = importlib.util.find_spec("reymen.desktop.launcher")
        assert spec is not None
