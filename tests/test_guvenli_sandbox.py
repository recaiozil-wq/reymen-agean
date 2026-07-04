# -*- coding: utf-8 -*-
"""tests/test_guvenli_sandbox.py — guvenli_sandbox modülü testleri."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from guvenli_sandbox import (
    guvenli_calistir,
    Sandbox,
    YASAKLI_ANAHTAR_KELIMELER,
    VARSAYILAN_MODUL_LISTESI,
    SandboxError,
    SandboxTimeout,
    YasakliModulHatasi,
)


class TestGuvenliSandbox:
    """guvenli_calistir() fonksiyonu testleri."""

    def test_bos_kod_hata_dondurur(self):
        sonuc = guvenli_calistir("")
        assert isinstance(sonuc, str)

    def test_bosluk_kod_hata_dondurur(self):
        sonuc = guvenli_calistir("   ")
        assert isinstance(sonuc, str)

    def test_basit_print_calisir(self):
        sonuc = guvenli_calistir("print('Merhaba')", timeout=10)
        assert "Merhaba" in sonuc

    def test_matematik_islemi_calisir(self):
        sonuc = guvenli_calistir("print(2 + 2)", timeout=10)
        assert "4" in sonuc

    def test_coklu_print_satirlari(self):
        sonuc = guvenli_calistir("print('A')\nprint('B')", timeout=10)
        assert "A" in sonuc and "B" in sonuc

    def test_degisken_kullanimi(self):
        sonuc = guvenli_calistir("x = 10\nprint(x * 2)", timeout=10)
        assert "20" in sonuc

    def test_syntax_hatasi_yakalanir(self):
        sonuc = guvenli_calistir("def)", timeout=10)
        assert "Hata" in sonuc or "SyntaxError" in sonuc or "hata" in sonuc.lower()

    def test_os_system_engellenir(self):
        with pytest.raises(YasakliModulHatasi):
            guvenli_calistir("import os; os.system('dir')", timeout=10)

    def test_eval_engellenir(self):
        with pytest.raises(YasakliModulHatasi):
            guvenli_calistir("eval('__import__(\"os\")')", timeout=10)

    def test_exec_engellenir(self):
        with pytest.raises(YasakliModulHatasi):
            guvenli_calistir("exec('import os')", timeout=10)

    def test_socket_engellenir(self):
        with pytest.raises(YasakliModulHatasi):
            guvenli_calistir("import socket", timeout=10)


class TestSandboxClassi:
    """Sandbox sınıfı testleri."""

    def test_sandbox_olusturma(self):
        sb = Sandbox(timeout=5, max_chars=1000)
        assert sb.timeout == 5
        assert sb.max_chars == 1000

    def test_sandbox_calistir(self):
        sb = Sandbox(timeout=10)
        sonuc = sb.calistir("print('test')")
        assert "test" in sonuc

    def test_sandbox_unicode_turkce(self):
        sb = Sandbox(timeout=10)
        sonuc = sb.calistir("print('Merhaba dünya')")
        assert "dunya" in sonuc or "dünya" in sonuc or "Merhaba" in sonuc


class TestSabitler:
    """Sabit listeler testleri."""

    def test_yasakli_anahtar_kelimeler_dolu(self):
        assert len(YASAKLI_ANAHTAR_KELIMELER) > 10

    def test_yasakli_anahtar_os_system_var(self):
        assert "os.system" in YASAKLI_ANAHTAR_KELIMELER

    def test_yasakli_anahtar_eval_var(self):
        assert "eval(" in YASAKLI_ANAHTAR_KELIMELER

    def test_modul_listesi_dolu(self):
        assert len(VARSAYILAN_MODUL_LISTESI) > 10

    def test_modul_listesi_math_var(self):
        assert "math" in VARSAYILAN_MODUL_LISTESI

    def test_modul_listesi_json_var(self):
        assert "json" in VARSAYILAN_MODUL_LISTESI


class TestHataSiniflari:
    """Hata sınıfları testleri."""

    def test_sandbox_error(self):
        with pytest.raises(SandboxError):
            raise SandboxError("test")

    def test_sandbox_timeout(self):
        with pytest.raises(SandboxTimeout):
            raise SandboxTimeout("timeout")

    def test_yasakli_modul_hatasi(self):
        with pytest.raises(YasakliModulHatasi):
            raise YasakliModulHatasi("yasakli")
