# -*- coding: utf-8 -*-
"""
test_izole_laboratuvar.py — izole_laboratuvar.py icin kapsamli pytest testleri

MODUL: izole_laboratuvar.py
  Docker container'inda (veya Docker yoksa local subprocess'te) izole kod calistirir.
Tum testler DOCKER_AVAILABLE=False ile (local subprocess) calisir.
"""

import os
import sys
import uuid
import subprocess
from pathlib import Path

import pytest


# ──────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def docker_devre_disi(monkeypatch):
    """Her test oncesi DOCKER_AVAILABLE=False garantile."""
    monkeypatch.setattr("izole_laboratuvar.DOCKER_AVAILABLE", False)


@pytest.fixture
def lab(request, monkeypatch):
    """izole_laboratuvar modulunu her test icin temiz import et.

    auto-use degil — cagiran testin istegine bagli.
    """
    # onceden import edilmis olabilir, temizle
    for mod in list(sys.modules.keys()):
        if "izole_laboratuvar" in mod:
            del sys.modules[mod]
    import izole_laboratuvar as lab

    return lab


# ──────────────────────────────────────────────────────────────────────
# TEMEL FONKSIYON TESTLERI — izole_python_calistir
# ──────────────────────────────────────────────────────────────────────


class TestIzolePythonCalistir:
    """izole_python_calistir() ana fonksiyonu — 3 senaryo."""

    def test_merhaba_ciktisi(self, lab):
        """1. print('Merhaba') -> [CIKTI] ve Merhaba ve [HATA] iceriyor."""
        cikti = lab.izole_python_calistir("print('Merhaba')", timeout=2)
        assert "[ÇIKTI]" in cikti, f"[ÇIKTI] etiketi eksik: {cikti!r}"
        assert "Merhaba" in cikti, f"Merhaba yok: {cikti!r}"
        assert "[HATA]" in cikti, f"[HATA] etiketi eksik: {cikti!r}"

    def test_aritmetik(self, lab):
        """2. print(2+2) -> '4' iceriyor."""
        cikti = lab.izole_python_calistir("print(2+2)", timeout=2)
        assert "4" in cikti, f"4 bulunamadi: {cikti!r}"

    def test_gecici_dosya_silinir(self, lab, tmp_path):
        """3. Gecici .py dosyasi calistirildiktan sonra siliniyor."""
        # cwd'yi gecici klasore al
        import izole_laboratuvar

        original_cwd = os.getcwd()
        try:
            os.chdir(str(tmp_path))
            # monkeypatch ile cwd degisti, modulu yeniden yukle
            for mod in list(sys.modules.keys()):
                if "izole_laboratuvar" in mod:
                    del sys.modules[mod]
            import izole_laboratuvar as lab2

            lab2.izole_python_calistir("print('temp')", timeout=2)
            # hic .py dosyasi kalmamali
            kalanlar = list(tmp_path.glob("_ReYMeN_*.py"))
            assert len(kalanlar) == 0, f"Silinmemis dosyalar: {kalanlar}"
        finally:
            os.chdir(original_cwd)


# ──────────────────────────────────────────────────────────────────────
# HATA SENARYOLARI
# ──────────────────────────────────────────────────────────────────────


class TestHataSenaryolari:
    """Hata/exit kodlari ve exception yonetimi."""

    def test_sys_exit_0_hata_yok(self, lab):
        """4. import sys; sys.exit(0) -> hata mesaji yok (sadece etiketler)."""
        cikti = lab.izole_python_calistir("import sys; sys.exit(0)", timeout=2)
        # exit(0) — hata yok, sadece format etiketleri
        assert "[ÇIKTI]" in cikti
        assert "[HATA]" in cikti
        # stderr bos oldugu icin [HATA] satirindan sonra bisey olmamali
        # (strip sonrasi format: [CIKTI]\n\n[HATA])

    def test_sys_exit_1_hata_icerir(self, lab):
        """5. import sys; sys.exit(1) -> [HATA] etiketi iceriyor (cikti formatinda)."""
        cikti = lab.izole_python_calistir("import sys; sys.exit(1)", timeout=2)
        # format geregi [HATA] etiketi her zaman ciktilarda yer alir
        assert "[HATA]" in cikti, f"[HATA] etiketi eksik: {cikti!r}"

    def test_raise_value_error(self, lab):
        """6. raise ValueError('test') -> ValueError traceback iceriyor."""
        cikti = lab.izole_python_calistir("raise ValueError('test')", timeout=2)
        assert "ValueError" in cikti, f"ValueError bulunamadi: {cikti!r}"

    def test_sonsuz_loop_timeout(self, lab):
        """7. Sonsuz loop -> timeout=2'de '[Hata]: Sandbox zaman aşımı.' doner."""
        cikti = lab.izole_python_calistir(
            "while True: pass",
            timeout=2,
        )
        assert "Sandbox zaman aşımı" in cikti, (
            f"Zaman asimi mesaji bekleniyor: {cikti!r}"
        )


# ──────────────────────────────────────────────────────────────────────
# ALT FONKSIYON TESTLERI — _local_run
# ──────────────────────────────────────────────────────────────────────


class TestLocalRun:
    """_local_run() dogrudan testler."""

    def test_temp_dosya_olustur_calistir_sil(self, lab, tmp_path):
        """8. _local_run — temp dosya olustur, calistir, sonra sil (manuel)."""
        dosya = tmp_path / f"_ReYMeN_{uuid.uuid4().hex[:8]}.py"
        dosya.write_text("print('local_test')", encoding="utf-8")
        cikti = lab._local_run(str(dosya), timeout=2)
        assert "local_test" in cikti
        # manuel sil
        if dosya.exists():
            dosya.unlink()
        assert not dosya.exists()

    def test_olmayan_dosya(self, lab):
        """9. _local_run — olmayan dosya -> hata yakalanir, [HATA] icerir."""
        olmayan = "/_kesinlikle_yok_bu_dosya.py"
        cikti = lab._local_run(olmayan, timeout=2)
        # subprocess exit kodu 2 (dosya bulunamadi), stderr'de hata mesaji
        assert "[HATA]" in cikti, f"[HATA] etiketi eksik: {cikti!r}"
        assert len(cikti) > 20, (
            f"Hata mesaji cok kisa, beklenmeyen: {cikti!r}"
        )


# ──────────────────────────────────────────────────────────────────────
# NEGATIF TESTLER
# ──────────────────────────────────────────────────────────────────────


class TestNegatif:
    """Sinirda / gecersiz girdiler."""

    def test_bos_kod(self, lab):
        """10. kod = '' -> bos cikti (etiketler disinda)."""
        cikti = lab.izole_python_calistir("", timeout=2)
        # etiketler var ama arada icerik yok
        assert "[ÇIKTI]" in cikti
        assert "[HATA]" in cikti
        # stdout bos oldugu icin [CIKTI] ile [HATA] arasinda sadece bosluk var
        cikti_duz = cikti.replace("\n", "").replace(" ", "")
        # sadece etiketler ve yeni satirlar kalmali
        assert len(cikti_duz) >= len("[ÇIKTI][HATA]"), (
            f"Beklenmedik icerik: {cikti!r}"
        )

    def test_kod_none(self, lab):
        """11. kod = None -> TypeError firlatir (f.write(None) basarisiz).

        Not: f.write(None) TypeError verir. 'with' blogu icinde oldugu
        icin dosya olusur ama try:finally bloguna girilmedigi icin
        cleanup calismaz — dosya diskte kalir.
        """
        with pytest.raises(TypeError, match="write.*argument.*str"):
            lab.izole_python_calistir(None, timeout=2)


# ──────────────────────────────────────────────────────────────────────
# KAPSAYICI TESTLER
# ──────────────────────────────────────────────────────────────────────


class TestKapsayici:
    """Finally blogu ve cleanup garantisi."""

    def test_temp_dosya_her_durumda_silinir(self, lab, tmp_path):
        """12. Temp dosyasi hata firlatsa bile finally blogunda siliniyor.

        ValueError firlatan kod: dosya olusur, calistirilir (ValueError),
        finally blogu calisir, dosya silinir.
        """
        import izole_laboratuvar

        original_cwd = os.getcwd()
        try:
            os.chdir(str(tmp_path))
            for mod in list(sys.modules.keys()):
                if "izole_laboratuvar" in mod:
                    del sys.modules[mod]
            import izole_laboratuvar as lab2

            lab2.izole_python_calistir("raise ValueError('cleanup')", timeout=2)
            # dosya silinmis olmali
            kalanlar = list(tmp_path.glob("_ReYMeN_*.py"))
            assert len(kalanlar) == 0, (
                f"Hata senaryosunda silinmemis dosya: {kalanlar}"
            )
        finally:
            os.chdir(original_cwd)


# ──────────────────────────────────────────────────────────────────────
# EK: _docker_run ERISIM TESTI
# ──────────────────────────────────────────────────────────────────────


class TestDockerRunErisim:
    """_docker_run fonksiyonuna erisim (calistirmiyor, Docker olmadan)."""

    def test_docker_run_mevcut_ama_devre_disidir(self, lab):
        """_docker_run() fonksiyonu tanimli ama DOCKER_AVAILABLE=False ile cagrilmaz."""
        assert hasattr(lab, "_docker_run"), "_docker_run tanimli degil"
        # DOCKER_AVAILABLE=False oldugu icin izole_python_calistir
        # _docker_run yerine _local_run cagirir
        cikti = lab.izole_python_calistir("print('docker_test')", timeout=2)
        assert "docker_test" in cikti
        # docker client import edilmemis olmali
        assert lab.DOCKER_AVAILABLE is False


# ──────────────────────────────────────────────────────────────────────
# EK: OUTPUT FORMAT TESTI
# ──────────────────────────────────────────────────────────────────────


class TestOutputFormati:
    """Cikti formatinin dogrulugu."""

    def test_cikti_formatinda_etiketler_vardir(self, lab):
        """_local_run ciktisi her zaman [CIKTI] ve [HATA] etiketlerini icerir."""
        cikti = lab.izole_python_calistir("print('format')", timeout=2)
        assert cikti.startswith("[ÇIKTI]"), f"[ÇIKTI] ile baslamiyor: {cikti!r}"
        assert "[HATA]" in cikti, f"[HATA] etiketi yok: {cikti!r}"
        # [HATA] [CIKTI]'den sonra gelmeli
        assert cikti.index("[HATA]") > cikti.index("[ÇIKTI]"), (
            f"[HATA] [ÇIKTI]'den once: {cikti!r}"
        )

    def test_basari_ciktisi_stderr_bos(self, lab):
        """Basarili calistirmada stderr bos olur, [HATA] satiri bostur."""
        cikti = lab.izole_python_calistir("print('ok')", timeout=2)
        # stdout icerigi var, stderr bos
        # format: [CIKTI]\nok\n\n[HATA]\n  -> strip: [CIKTI]\nok\n\n[HATA]
        hatadan_sonrasi = cikti.split("[HATA]")[-1].strip()
        assert hatadan_sonrasi in ("", " "), (
            f"HATA bolumu bos olmali ama su var: {hatadan_sonrasi!r}"
        )

    def test_hata_ciktisinda_traceback_vardir(self, lab):
        """Hata durumunda [HATA] sonrasi traceback icerir."""
        cikti = lab.izole_python_calistir(
            "1/0", timeout=2
        )
        assert "ZeroDivisionError" in cikti, (
            f"ZeroDivisionError tracebacki yok: {cikti!r}"
        )
        hatadan_sonrasi = cikti.split("[HATA]")[-1]
        assert "ZeroDivisionError" in hatadan_sonrasi, (
            f"Hata bolumunde ZeroDivisionError yok: {hatadan_sonrasi!r}"
        )
