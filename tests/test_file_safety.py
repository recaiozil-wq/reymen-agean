# -*- coding: utf-8 -*-
"""tests/test_file_safety.py — file_safety modülü testleri."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from file_safety import (
    guvenli_mi,
    YASAK_DIZINLER,
    YASAK_UZANTILAR,
    YASAK_DOSYALAR,
)


class TestFileSafetyConstants:
    """YASAK sabit listeleri testleri."""

    def test_yasak_dizinler_dolu(self):
        assert len(YASAK_DIZINLER) >= 10

    def test_yasak_dizinler_windows_var(self):
        windows_dizinleri = [d for d in YASAK_DIZINLER if "Windows" in d]
        assert len(windows_dizinleri) >= 1

    def test_yasak_dizinler_etc_var(self):
        assert any("/etc" in d for d in YASAK_DIZINLER)

    def test_yasak_uzantilar_dolu(self):
        assert len(YASAK_UZANTILAR) >= 5

    def test_yasak_uzantilar_exe_var(self):
        assert ".exe" in YASAK_UZANTILAR

    def test_yasak_uzantilar_dll_var(self):
        assert ".dll" in YASAK_UZANTILAR

    def test_yasak_dosyalar_dolu(self):
        assert len(YASAK_DOSYALAR) >= 5

    def test_yasak_dosyalar_boot_ini_var(self):
        assert "boot.ini" in YASAK_DOSYALAR


class TestGuvenliMi:
    """guvenli_mi() fonksiyonu testleri."""

    def test_guvenli_txt_dosyasi(self):
        guvenli, mesaj = guvenli_mi("test.txt")
        assert guvenli is True

    def test_guvenli_py_dosyasi(self):
        guvenli, _ = guvenli_mi("script.py")
        assert guvenli is True

    def test_guvenli_md_dosyasi(self):
        guvenli, _ = guvenli_mi("README.md")
        assert guvenli is True

    def test_yasak_exe_dosyasi(self):
        guvenli, mesaj = guvenli_mi("test.exe")
        assert guvenli is False
        assert "exe" in mesaj.lower() or "tur" in mesaj.lower()

    def test_yasak_dll_dosyasi(self):
        guvenli, mesaj = guvenli_mi("test.dll")
        assert guvenli is False

    def test_yasak_bat_dosyasi(self):
        guvenli, mesaj = guvenli_mi("test.bat")
        assert guvenli is False

    def test_yasak_cmd_dosyasi(self):
        guvenli, mesaj = guvenli_mi("test.cmd")
        assert guvenli is False

    def test_yasak_dizin_windows(self):
        guvenli, mesaj = guvenli_mi("C:\\Windows\\System32\\test.txt")
        assert guvenli is False

    def test_yasak_dizin_etc(self):
        guvenli, mesaj = guvenli_mi("/etc/passwd")
        assert guvenli is False

    def test_path_traversal(self):
        guvenli, mesaj = guvenli_mi("../../../etc/passwd")
        assert guvenli is False

    def test_guvenli_uzun_yol(self):
        guvenli, _ = guvenli_mi("docs/proje/notlar.md")
        assert guvenli is True
