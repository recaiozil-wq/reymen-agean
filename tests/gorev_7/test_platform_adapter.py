"""Platform adapter birim testleri."""

from __future__ import annotations

import subprocess
import sys

import pytest

from reymen import platform_adapter
from reymen.platform_adapter import (
    NativeAdapter,
    WSLAdapter,
    KaliAdapter,
    PlatformAdapter,
    set_adapter,
)


class TestWSLPathTranslation:
    @pytest.fixture
    def adapter(self):
        return WSLAdapter(distro="Ubuntu")

    def test_drive_letter_to_mnt(self, adapter):
        assert adapter.translate_path(r"C:\Users\foo") == "/mnt/c/Users/foo"

    def test_drive_letter_lower(self, adapter):
        assert adapter.translate_path(r"D:\data\file.txt") == "/mnt/d/data/file.txt"

    def test_wsl_unc_path(self, adapter):
        assert adapter.translate_path(r"\\wsl$\Ubuntu\home\user") == "/home/user"

    def test_wsl_localhost_unc(self, adapter):
        assert (
            adapter.translate_path(r"\\wsl.localhost\Ubuntu\home\user") == "/home/user"
        )

    def test_linux_path_unchanged(self, adapter):
        assert adapter.translate_path("/home/user/file") == "/home/user/file"

    def test_tilde_path_unchanged(self, adapter):
        assert adapter.translate_path("~/documents") == "~/documents"


class TestWSLPathBackTranslation:
    @pytest.fixture
    def adapter(self):
        return WSLAdapter(distro="Ubuntu")

    def test_mnt_to_drive(self, adapter):
        assert adapter.translate_path_back("/mnt/c/Users/foo") == r"C:\Users\foo"

    def test_linux_path_to_unc(self, adapter):
        result = adapter.translate_path_back("/home/user")
        assert result == r"\\wsl$\Ubuntu\home\user"


class TestNativeAdapter:
    def test_translate_path_identity(self):
        adapter = NativeAdapter()
        assert adapter.translate_path("/some/path") == "/some/path"
        assert adapter.translate_path(r"C:\some\path") == r"C:\some\path"

    def test_run_echo(self):
        adapter = NativeAdapter()
        result = adapter.run([sys.executable, "-c", "print('hello')"])
        assert result.returncode == 0
        assert "hello" in result.stdout


class TestKaliAdapter:
    def test_kind(self):
        adapter = KaliAdapter()
        assert adapter.kind == "kali"

    def test_distro(self):
        adapter = KaliAdapter()
        assert adapter.distro == "kali-linux"

    def test_inherits_wsl_path_translation(self):
        adapter = KaliAdapter()
        assert adapter.translate_path(r"C:\Users\foo") == "/mnt/c/Users/foo"


class TestDetect:
    def test_detect_returns_adapter(self):
        adapter = platform_adapter.detect()
        assert isinstance(adapter, PlatformAdapter)

    def test_detect_non_windows_returns_native(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")
        adapter = platform_adapter.detect()
        assert isinstance(adapter, NativeAdapter)


class TestModuleLevel:
    def test_set_and_get_adapter(self):
        original = platform_adapter._get_adapter()
        try:
            custom = NativeAdapter()
            set_adapter(custom)
            assert platform_adapter._get_adapter() is custom
        finally:
            set_adapter(original)

    def test_translate_path_uses_singleton(self):
        adapter = NativeAdapter()
        set_adapter(adapter)
        assert platform_adapter.translate_path("/foo") == "/foo"
