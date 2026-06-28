"""execute_code_tool.py için testler."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execute_code_tool import run, check_fn, TOOL_META, _guvenlik_kontrol


class TestMeta:
    def test_meta_var(self):
        assert TOOL_META is not None
        assert TOOL_META["ad"] == "execute_code"

    def test_meta_parametreler(self):
        assert "kod" in TOOL_META["parametreler"]
        assert TOOL_META["parametreler"]["kod"]["zorunlu"] is True

    def test_meta_kategori(self):
        assert TOOL_META["kategori"] == "orkestrasyon"


class TestGuvenlikKontrol:
    def test_guvenli_kod(self):
        gecerli, hata = _guvenlik_kontrol("print('merhaba')")
        assert gecerli is True
        assert hata == ""

    def test_os_system_engellenir(self):
        gecerli, hata = _guvenlik_kontrol("os.system('ls')")
        assert gecerli is False
        assert "Güvenlik" in hata

    def test_subprocess_engellenir(self):
        gecerli, hata = _guvenlik_kontrol("subprocess.run('ls')")
        assert gecerli is False

    def test_open_engellenir(self):
        gecerli, hata = _guvenlik_kontrol("open('/etc/passwd')")
        assert gecerli is False

    def test_eval_engellenir(self):
        gecerli, hata = _guvenlik_kontrol("eval('1+1')")
        assert gecerli is False

    def test_exec_engellenir(self):
        gecerli, hata = _guvenlik_kontrol("exec('print(1)')")
        assert gecerli is False


class TestRun:
    def test_basit_print(self):
        sonuc = run("print('merhaba dunya')")
        assert "merhaba dunya" in sonuc
        assert "✅" in sonuc

    def test_aritmetik(self):
        sonuc = run("print(sum(range(10)))")
        assert "45" in sonuc

    def test_hata_yakalama(self):
        sonuc = run("print(1/0)")
        assert "❌" in sonuc
        assert "ZeroDivisionError" in sonuc

    def test_coklu_print(self):
        sonuc = run("print('a')\nprint('b')\nprint('c')")
        assert "a" in sonuc
        assert "b" in sonuc
        assert "c" in sonuc

    def test_degisken_kullanimi(self):
        sonuc = run("x = 42\ny = x * 2\nprint(y)")
        assert "84" in sonuc

    def test_string_islemleri(self):
        sonuc = run("""s = "hermes"\nprint(s.upper())""")
        assert "HERMES" in sonuc

    def test_liste_islemleri(self):
        sonuc = run("print([i*2 for i in range(5)])")
        assert "[0, 2, 4, 6, 8]" in sonuc

    def test_guvenlik_engellemesi(self):
        sonuc = run("import os; os.system('echo test')")
        assert "GUVENLIK_REDDI" in sonuc

    def test_bos_kod(self):
        sonuc = run("")
        assert "çıktı yok" in sonuc or "✅" in sonuc


class TestCheckFn:
    def test_basarili(self):
        ok, mesaj = check_fn({"kod": "print('test')"})
        assert ok is True

    def test_basarisiz(self):
        ok, mesaj = check_fn({})
        assert ok is False
        assert "zorunludur" in mesaj

    def test_bos_kod_param(self):
        ok, mesaj = check_fn({"kod": ""})
        assert ok is False

    def test_ekstra_parametreler(self):
        ok, mesaj = check_fn({"kod": "print(1)", "timeout": 10, "x": "y"})
        assert ok is True


class TestEdgeCases:
    def test_unicode_kod(self):
        sonuc = run("print('ğüşıöç İŞĞÜ')")
        assert "ğüşıöç" in sonuc

    def test_buyuk_cikti(self):
        """Büyük çıktı üreten kod çalışabilmeli."""
        sonuc = run("for i in range(100): print(i)")
        assert "99" in sonuc
        assert "0" in sonuc

    def test_import_math(self):
        """math modülü import edilebilmeli."""
        sonuc = run("import math; print(math.pi)")
        assert "3.14" in sonuc

    def test_import_guvenli(self):
        """Modül import edilebilir olmalı."""
        import execute_code_tool
        assert hasattr(execute_code_tool, "run")
        assert hasattr(execute_code_tool, "check_fn")
        assert hasattr(execute_code_tool, "TOOL_META")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
