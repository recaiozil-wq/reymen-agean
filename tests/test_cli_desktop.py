"""Test: reymen/cli.py desktop subcommand + extra desktop integration."""

from __future__ import annotations
import os
import sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestCLIDesktop:
    def test_cli_build_parser(self):
        from reymen.cli import build_parser

        parser = build_parser()
        assert parser is not None

    def test_cli_desktop_parser(self):
        from reymen.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["desktop", "status"])
        assert args.desktop_cmd == "status"
        assert args.func is not None

    def test_cli_desktop_func_returns(self):
        from reymen.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["desktop", "status"])
        result = args.func(args)
        assert isinstance(result, str)
        assert "Durum" in result

    def test_cli_desktop_start_has_func(self):
        from reymen.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["desktop", "start"])
        assert args.func is not None

    def test_cli_desktop_stop_has_func(self):
        from reymen.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["desktop", "stop"])
        assert args.func is not None

    def test_cli_desktop_autostart_has_func(self):
        from reymen.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["desktop", "autostart"])
        assert args.func is not None

    def test_desktop_launcher_main(self):
        from reymen.desktop.launcher import main

        assert callable(main)


class TestDesktopCLICommands:
    def test_desktop_server_import_and_api(self):
        from reymen.desktop.server import web_server

        assert hasattr(web_server, "start")
        assert hasattr(web_server, "stop")
        assert hasattr(web_server, "status")
        assert hasattr(web_server, "url")

    def test_desktop_server_status(self):
        from reymen.desktop.server import web_server

        status = web_server.status
        assert status in ("running", "stopped")

    def test_desktop_server_url(self):
        from reymen.desktop.server import web_server

        assert "127.0.0.1" in web_server.url
