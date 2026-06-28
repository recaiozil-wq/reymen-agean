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
        """Yasak dizin listesi en az 10 öğe içermeli."""
        assert len(YASAK_DIZINLER) >= 10

    def test_yasak_dizinler_windows_var(self):
        """Windows sistem dizini listede olmalı."""
        windows_dizinleri = [d for d in YASAK_DIZINLER if "Windows" in d]
        assert len(windows_dizinleri) >= 1

    def test_yasak_dizinler_etc_var(self):
        """/etc dizini listede olmalı."""
        assert any("/etc" in d for d in YASAK_DIZINLER)

    def test_yasak_uzantilar_dolu(self):
        """Yasak uzantı listesi en az 8 öğe içermeli."""
        assert len(YASAK_UZANTILAR) >= 8

    def test_yasak_uzantilar_exe_var(self):
        """.exe yasak uzantıda olmalı."""
        assert ".exe" in YASAK_UZANTILAR

    def test_yasak_uzantilar_dll_var(self):
        """.dll yasak uzantıda olmalı."""
        assert ".dll" in YASAK_UZANTILAR

    def test_yasak_uzantilar_bat_var(self):
        """.bat yasak uzantıda olmalı."""
        assert ".bat" in YASAK_UZANTILAR

    def test_yasak_uzantilar_ps1_var(self):
        """.ps1 yasak uzantıda olmalı."""
        assert ".ps1" in YASAK_UZANTILAR

    def test_yasak_dosyalar_dolu(self):
        """Yasak dosya listesi en az 5 öğe içermeli."""
        assert len(YASAK_DOSYALAR) >= 5

    def test_yasak_dosyalar_hosts_var(self):
        """"hosts" yasak dosyalarda olmalı."""
        assert "hosts" in YASAK_DOSYALAR

    def test_yasak_dosyalar_env_var(self):
        """.env yasak dosyalarda olmalı."""
        assert ".env" in YASAK_DOSYALAR

    def test_yasak_dosyalar_passwd_var(self):
        """"passwd" yasak dosyalarda olmalı."""
        assert "passwd" in YASAK_DOSYALAR


class TestGuvenliMi:
    """guvenli_mi() fonksiyonu testleri."""

    # ── Güvenli dosyalar ──────────────────────────────────────────────────

    def test_guvenli_txt_dosyasi(self):
        """Normal .txt dosyası güvenli sayılmalı."""
        guvenli, mesaj = guvenli_mi("test.txt")
        assert guvenli is True
        assert mesaj == "Güvenli"

    def test_guvenli_py_dosyasi(self):
        """.py dosyası güvenli sayılmalı."""
        guvenli, _ = guvenli_mi("script.py")
        assert guvenli is True

    def test_guvenli_md_dosyasi(self):
        """.md dosyası güvenli sayılmalı."""
        guvenli, _ = guvenli_mi("README.md")
        assert guvenli is True

    def test_guvenli_klasor_yolu(self):
        """Klasör yolu güvenli sayılmalı."""
        guvenli, _ = guvenli_mi("C:\\Users\\marko\\Documents\\")
        # Kullanıcı dizini yasak dizinlerde yoksa güvenli
        assert guvenli is True

    def test_guvenli_relative_yol(self):
        """Göreceli yol güvenli sayılmalı."""
        guvenli, _ = guvenli_mi("data/dosya.txt")
        assert guvenli is True

    # ── Yasak uzantılar ──────────────────────────────────────────────────

    def test_exe_yasak(self):
        """.exe dosyası yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("zararli.exe")
        assert guvenli is False
        assert "Yasak uzantı" in mesaj

    def test_dll_yasak(self):
        """.dll dosyası yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("library.dll")
        assert guvenli is False
        assert "Yasak uzantı" in mesaj

    def test_bat_yasak(self):
        """.bat dosyası yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("script.bat")
        assert guvenli is False
        assert "Yasak uzantı" in mesaj

    def test_cmd_yasak(self):
        """.cmd dosyası yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("command.cmd")
        assert guvenli is False
        assert "Yasak uzantı" in mesaj

    def test_vbs_yasak(self):
        """.vbs dosyası yasaklanmalı."""
        guvenli, _ = guvenli_mi("script.vbs")
        assert guvenli is False

    def test_ps1_yasak(self):
        """.ps1 dosyası yasaklanmalı."""
        guvenli, _ = guvenli_mi("script.ps1")
        assert guvenli is False

    def test_msi_yasak(self):
        """.msi dosyası yasaklanmalı."""
        guvenli, _ = guvenli_mi("setup.msi")
        assert guvenli is False

    def test_scr_yasak(self):
        """.scr dosyası yasaklanmalı."""
        guvenli, _ = guvenli_mi("screen.scr")
        assert guvenli is False

    # ── Yasak dizinler ────────────────────────────────────────────────────

    def test_windows_system32_yasak(self):
        """C:\\Windows\\System32 altı yasaklanmalı (uzantı veya dizin)."""
        guvenli, mesaj = guvenli_mi("C:\\Windows\\System32\\config.dll")
        assert guvenli is False
        # Ya uzantı (.dll) ya da dizin (System32) kontrolü çalışır
        assert mesaj

    def test_windows_dizini_yasak(self):
        """C:\\Windows altı yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("C:\\Windows\\system.ini")
        assert guvenli is False
        assert "Yasak dizin" in mesaj

    def test_program_files_yasak(self):
        """C:\\Program Files altı yasaklanmalı."""
        guvenli, _ = guvenli_mi("C:\\Program Files\\test.exe")
        assert guvenli is False

    def test_etc_dizini_yasak(self):
        """/etc/passwd yasaklanmalı (dosya adı veya dizin)."""
        guvenli, mesaj = guvenli_mi("/etc/passwd")
        assert guvenli is False
        # passwd yasak dosya adıdır, ya da /etc yasak dizindir
        assert mesaj

    # ── Yasak dosya adları ────────────────────────────────────────────────

    def test_hosts_dosyasi_yasak(self):
        """hosts dosyası yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("C:\\Windows\\System32\\drivers\\etc\\hosts")
        assert guvenli is False

    def test_passwd_dosyasi_yasak(self):
        """passwd dosyası yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("/etc/passwd")
        assert guvenli is False

    def test_env_dosyasi_yasak(self):
        """.env dosyası yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("/proje/.env")
        assert guvenli is False
        assert "Yasak dosya" in mesaj

    # ── Path traversal ────────────────────────────────────────────────────

    def test_path_traversal_yasak(self):
        """Path traversal (..) içeren yol yasaklanmalı."""
        guvenli, _ = guvenli_mi("data/../../etc/x.txt")
        assert guvenli is False

    def test_path_traversal_basit(self):
        """Basit path traversal yasaklanmalı."""
        guvenli, mesaj = guvenli_mi("../disari.txt")
        assert guvenli is False
        assert "Path traversal" in mesaj

    # ── Kenar durumlar ────────────────────────────────────────────────────

    def test_bos_yol(self):
        """Boş yolun nasıl işlendiğini kontrol et."""
        guvenli, mesaj = guvenli_mi("")
        # Path("") çalışma dizinine çözümlenir, bu yüzden güvenli olabilir
        # Önemli olan bir tuple dönmesi
        assert isinstance(guvenli, bool)
        assert isinstance(mesaj, str)

    def test_unicode_yol(self):
        """Unicode karakterli yol."""
        guvenli, _ = guvenli_mi("şğıüöç/dosya.txt")
        assert guvenli is True

    def test_cok_uzun_uzanti(self):
        """Uzun/yok uzantı güvenli sayılmalı."""
        guvenli, _ = guvenli_mi("dosya.")
        assert guvenli is True

    def test_ntfs_alternatif_akis(self):
        """NTFS alternatif akış yolu güvenli mi? (varsayılan: izin ver)."""
        guvenli, _ = guvenli_mi("dosya.txt:hassas")
        # Path oluşturmada sorun çıkmazsa True döner
        assert guvenli is True

    def test_absolute_python_yolu_guvenli(self):
        """Mutlak Python dosya yolu güvenli sayılmalı (yasak dizinde değilse)."""
        guvenli, _ = guvenli_mi("C:\\Projects\\test.py")
        assert guvenli is True

    def test_cd_ust_dizin_traversal(self):
        """'..\\' ile başlayan yol traversal tespit edilmeli."""
        guvenli, mesaj = guvenli_mi("..\\etc\\passwd")
        assert guvenli is False
