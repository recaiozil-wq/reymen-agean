"""Test: reymen/web_ui/sandbox.py"""

from __future__ import annotations
import os, sys, tempfile
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSandbox:
    def test_import(self):
        from reymen.web_ui.sandbox import Sandbox

        assert Sandbox is not None

    def test_create_and_file_ops(self):
        from reymen.web_ui.sandbox import Sandbox

        with tempfile.TemporaryDirectory() as tmp:
            sb = Sandbox("test", Path(tmp))
            sb.dosya_yaz("a.txt", "hello")
            assert sb.dosya_oku("a.txt") == "hello"

    def test_rapor(self):
        from reymen.web_ui.sandbox import Sandbox

        with tempfile.TemporaryDirectory() as tmp:
            sb = Sandbox("test2", Path(tmp))
            assert isinstance(sb.rapor(), dict)

    def test_temizle(self):
        from reymen.web_ui.sandbox import Sandbox

        with tempfile.TemporaryDirectory() as tmp:
            sb = Sandbox("test3", Path(tmp))
            sb.dosya_yaz("x.txt", "data")
            sb.temizle()
            assert not (Path(tmp) / "x.txt").exists()
