# -*- coding: utf-8 -*-
"""tests/test_guvenli_sandbox.py — guvenli_sandbox modülü testleri."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGuvenliSandbox:
    """guvenli_sandbox.py birim testleri."""

    # ── Sabitler ve yardımcılar ────────────────────────────────────────────

    @pytest.fixture(autouse=True)
    def _modulu_yukle(self):
        from guvenli_sandbox import (
            guvenli_calistir,
            sandbox_modu_raporu,
            _tehlikeli_mi,
            _TEHLIKELI_KALIPLAR,
        )
        self.guvenli_calistir = guvenli_calistir
        self.sandbox_modu_raporu = sandbox_modu_raporu
        self._tehlikeli_mi = _tehlikeli_mi
        self._TEHLIKELI_KALIPLAR = _TEHLIKELI_KALIPLAR

    # ── Ana API: guvenli_calistir ──────────────────────────────────────────

    def test_bos_kod_hata_dondurur(self):
        """Boş kod girilince hata dönmeli."""
        sonuc = self.guvenli_calistir("")
        assert "[Hata]" in sonuc

    def test_bosluk_kod_hata_dondurur(self):
        """Sadece boşluk kod girilince hata dönmeli."""
        sonuc = self.guvenli_calistir("   ")
        assert "[Hata]" in sonuc

    def test_basit_print_calisir(self):
        """Basit print komutu çalışmalı, çıktıda [CIKTI] olmalı."""
        sonuc = self.guvenli_calistir("print('Merhaba')", timeout=10)
        assert "[CIKTI]" in sonuc or "Merhaba" in sonuc

    def test_matematik_islemi_calisir(self):
        """Matematik işlemi çalışmalı."""
        sonuc = self.guvenli_calistir("x = 2 ** 10\nprint(x)", timeout=10)
        assert "1024" in sonuc

    def test_coklu_print_satirlari(self):
        """Çok satırlı print çıktısı düzgün birleşmeli."""
        sonuc = self.guvenli_calistir("print('a')\nprint('b')\nprint('c')", timeout=10)
        assert "a" in sonuc and "b" in sonuc and "c" in sonuc

    def test_degisken_kullanimi(self):
        """Değişken tanımlama ve kullanma çalışmalı."""
        sonuc = self.guvenli_calistir("isim = 'Dunya'\nprint(f'Merhaba {isim}')", timeout=10)
        assert "Merhaba Dunya" in sonuc

    def test_syntax_hatasi_yakalanir(self):
        """Sözdizimi hatası uygun mesajla dönmeli."""
        sonuc = self.guvenli_calistir("def bozuk(\nprint('hata')", timeout=5)
        assert "[Hata]" in sonuc or "hata" in sonuc.lower()

    def test_zaman_asimi_calisir(self):
        """Sonsuz döngü zaman aşımına uğramalı."""
        sonuc = self.guvenli_calistir("import time\nwhile True: time.sleep(1)", timeout=2)
        assert "[Hata]" in sonuc or "zaman" in sonuc.lower()

    def test_kisa_timeout_calisir(self):
        """Çok kısa timeout ile bile çalışan kod düzgün tamamlanmalı."""
        sonuc = self.guvenli_calistir("print('hizli')", timeout=1)
        assert "hizli" in sonuc

    # ── Tehlike kontrolü ──────────────────────────────────────────────────

    def test_os_system_engellenir(self):
        """os.system() tehlikeli kalıp olarak engellenmeli."""
        sonuc = self.guvenli_calistir("import os\nos.system('echo kotu')", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_subprocess_engellenir(self):
        """subprocess çağrısı tehlikeli kalıp olarak engellenmeli."""
        sonuc = self.guvenli_calistir("import subprocess\nsubprocess.run(['dir'])", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_eval_engellenir(self):
        """eval() tehlikeli kalıp olarak engellenmeli."""
        sonuc = self.guvenli_calistir("eval('1+1')", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_exec_engellenir(self):
        """exec() tehlikeli kalıp olarak engellenmeli."""
        sonuc = self.guvenli_calistir("exec('x=1')", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_os_import_engellenir(self):
        """import os ile os komutu engellenmeli (os.system ile)."""
        sonuc = self.guvenli_calistir("import os\nos.system('echo test')", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_open_yazma_engellenir(self):
        """open() yazma modunda engellenmeli."""
        sonuc = self.guvenli_calistir("open('test.txt', 'w')", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_socket_engellenir(self):
        """socket kullanımı engellenmeli."""
        sonuc = self.guvenli_calistir("import socket\nsocket.socket()", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_requests_engellenir(self):
        """requests kullanımı engellenmeli."""
        sonuc = self.guvenli_calistir("import requests\nrequests.get('http://x.com')", timeout=5)
        assert "[Guvenlik Reddi]" in sonuc

    def test_tehlike_kontrolu_devre_disi(self):
        """tehlike_kontrolu=False ile tehlikeli kod çalışabilmeli (mod=tempdir ile)."""
        sonuc = self.guvenli_calistir(
            "import os\nprint('test')", timeout=5,
            mod="tempdir", tehlike_kontrolu=False
        )
        # os.system değil sadece import os + print, çalışması yeterli
        assert "test" in sonuc or "[CIKTI]" in sonuc

    # ── _tehlikeli_mi birim testleri ──────────────────────────────────────

    def test_tehlikeli_mi_temiz_kod(self):
        """Temiz kod tehlikeli sayılmamalı."""
        tehlikeli, kalip = self._tehlikeli_mi("print('merhaba')")
        assert not tehlikeli

    def test_tehlikeli_mi_os_system(self):
        """os.system içeren kod tehlikeli sayılmalı."""
        tehlikeli, kalip = self._tehlikeli_mi("os.system('ls')")
        assert tehlikeli
        assert "os.system" in kalip

    def test_tehlikeli_mi_eval(self):
        """eval() içeren kod tehlikeli sayılmalı."""
        tehlikeli, kalip = self._tehlikeli_mi("eval('1+1')")
        assert tehlikeli
        assert "eval" in kalip.lower()

    def test_tehlikeli_kaliplar_listesi_dolu(self):
        """Tehlikeli kalıp listesi en az 15 öğe içermeli."""
        assert len(self._TEHLIKELI_KALIPLAR) >= 15

    # ── mod parametresi (oto/docker/restricted/tempdir) ────────────────────

    def test_mod_tempdir_her_zaman_calisir(self):
        """mod='tempdir' her zaman çalışmalı (bağımlılık yok)."""
        sonuc = self.guvenli_calistir("print('tempdir test')", timeout=10, mod="tempdir")
        assert "tempdir test" in sonuc

    def test_mod_docker_yoksa_hata_doner(self):
        """mod='docker' seçilip Docker yoksa hata mesajı dönmeli."""
        sonuc = self.guvenli_calistir("print('docker test')", timeout=5, mod="docker")
        assert "Docker mevcut degil" in sonuc or "[CIKTI]" in sonuc

    def test_mod_restricted_yoksa_hata_doner(self):
        """mod='restricted' seçilip RestrictedPython yoksa hata dönmeli."""
        sonuc = self.guvenli_calistir("print('restricted test')", timeout=5, mod="restricted")
        assert "RestrictedPython" in sonuc or "[CIKTI]" in sonuc

    # ── sandbox_modu_raporu ──────────────────────────────────────────────

    def test_sandbox_modu_raporu_donuyor(self):
        """sandbox_modu_raporu() en az bir mod bildirmeli."""
        rapor = self.sandbox_modu_raporu()
        assert isinstance(rapor, str)
        assert "TempDir" in rapor

    def test_sandbox_raporu_uzunluk(self):
        """sandbox_modu_raporu() yeterli uzunlukta olmalı."""
        rapor = self.sandbox_modu_raporu()
        assert len(rapor) >= 20

    # ── Kenar durumlar ────────────────────────────────────────────────────

    def test_unicode_turkce_karakterler(self):
        """Türkçe karakterlerle print çalışmalı."""
        sonuc = self.guvenli_calistir("print('şğıüöç İstanbul')", timeout=10)
        assert "İstanbul" in sonuc or "şğıüöç" in sonuc

    def test_fonksiyon_tanimlama(self):
        """Fonksiyon tanımlayıp çağırma çalışmalı."""
        sonuc = self.guvenli_calistir(
            "def topla(a, b):\n    return a + b\nprint(topla(3, 5))",
            timeout=10
        )
        assert "8" in sonuc

    def test_liste_ve_dongu(self):
        """Liste ve döngü çalışmalı."""
        sonuc = self.guvenli_calistir(
            "toplam = sum(range(10))\nprint(toplam)",
            timeout=10
        )
        assert "45" in sonuc

    def test_dict_kullanimi(self):
        """Sözlük kullanımı çalışmalı."""
        sonuc = self.guvenli_calistir(
            "d = {'a': 1, 'b': 2}\nprint(d['a'] + d['b'])",
            timeout=10
        )
        assert "3" in sonuc

    def test_import_math_calisir(self):
        """Güvenli import (math) çalışmalı."""
        kod = "import math\nprint(math.sqrt(16))"
        sonuc = self.guvenli_calistir(kod, timeout=10)
        assert "4.0" in sonuc

    def test_cok_buyuk_sayi(self):
        """Büyük sayılarla işlem çalışmalı."""
        sonuc = self.guvenli_calistir("print(10 ** 100)", timeout=10)
        assert "1" in sonuc
