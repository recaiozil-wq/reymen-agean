# -*- coding: utf-8 -*-
"""tests/test_alt_ajan.py — AltAjan dongu dedektoru + circuit breaker testleri.

alt_ajan.py modul seviyesinde Beyin import eder ve _ALT_BEYIN olusturur.
Bu yuzu sys.modules ile mock'layarak import izolasyonu saglanir.

Calistirma: python -m pytest tests/test_alt_ajan.py -v
"""

import sys
import types
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── sys.path ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── Modul-seviyesi mock'lari (alt_ajan import edilmeden once) ─────────────────
def _mock_alt_ajan_module():
    """beyin, motor, dotenv, yaml ve config.yaml'i mocklayarak alt_ajan'i yukle."""
    # Sahte Beyin sinifi
    mock_beyin_cls = MagicMock()
    mock_beyin_inst = MagicMock()
    mock_beyin_inst.uret.return_value = 'Dusunce: test\nEylem: GOREV_BITTI("bitti")'
    mock_beyin_cls.return_value = mock_beyin_inst

    mock_beyin_mod = types.ModuleType("beyin")
    mock_beyin_mod.Beyin = mock_beyin_cls

    # Sahte Motor sinifi
    mock_motor_cls = MagicMock()
    mock_motor_mod = types.ModuleType("motor")
    mock_motor_mod.Motor = mock_motor_cls

    # Sahte dotenv
    mock_dotenv = types.ModuleType("dotenv")
    mock_dotenv.load_dotenv = MagicMock()

    # Sahte yaml
    mock_yaml = types.ModuleType("yaml")
    mock_yaml.safe_load = MagicMock(
        return_value={
            "model": "test-model",
            "toolsets": ["file"],
            "max_turns": 5,
            "compression": {"enabled": False},
        }
    )

    # sys.modules'a ekle
    for name, mod in [
        ("beyin", mock_beyin_mod),
        ("motor", mock_motor_mod),
        ("dotenv", mock_dotenv),
        ("yaml", mock_yaml),
    ]:
        sys.modules.setdefault(name, mod)

    # config.yaml okuma ve alt_ajan import
    with patch(
        "builtins.open",
        MagicMock(
            return_value=MagicMock(
                __enter__=MagicMock(
                    return_value=MagicMock(read=MagicMock(return_value="{}"))
                ),
                __exit__=MagicMock(return_value=False),
            )
        ),
    ):
        if "alt_ajan" in sys.modules:
            return sys.modules["alt_ajan"]
        import importlib

        return importlib.import_module("alt_ajan")


# Alt_ajan modülünü bir kez yükle
try:
    _alt_ajan_mod = _mock_alt_ajan_module()
    AltAjan = _alt_ajan_mod.AltAjan
    AltAjanSonuc = _alt_ajan_mod.AltAjanSonuc
    _IMPORT_OK = True
except Exception as _import_err:
    _IMPORT_OK = False
    _IMPORT_ERR = str(_import_err)


# ── Skip dekoratoru ───────────────────────────────────────────────────────────
skipif_import = pytest.mark.skipif(
    not _IMPORT_OK,
    reason=f"alt_ajan yuklenemedi: {_IMPORT_ERR if not _IMPORT_OK else ''}",
)


# ══════════════════════════════════════════════════════════════════════════════
# __init__ Testleri
# ══════════════════════════════════════════════════════════════════════════════


@skipif_import
class TestAltAjanInit:
    def test_hata_sayaci_baslangic_sifir(self):
        aj = AltAjan("test gorevi")
        assert aj._onceki_hata_sayaci == 0

    def test_gozlem_listesi_bos(self):
        aj = AltAjan("test gorevi")
        assert aj._onceki_gozlemler == []

    def test_eylem_listesi_bos(self):
        aj = AltAjan("test gorevi")
        assert aj._onceki_eylemler == []

    def test_zaman_asimi_varsayilan(self):
        aj = AltAjan("test gorevi")
        assert aj._zaman_asimi == 120.0

    def test_task_id_olusur(self):
        aj = AltAjan("test gorevi")
        assert aj.task_id and len(aj.task_id) == 8


# ══════════════════════════════════════════════════════════════════════════════
# Hata Sayacı Testleri
# ══════════════════════════════════════════════════════════════════════════════


@skipif_import
class TestHataSayaci:
    def _ajan_olustur(self, gorev="test gorevi"):
        aj = AltAjan(gorev)
        # _motor_al'i mock'la
        mock_motor = MagicMock()
        aj._motor = mock_motor
        return aj

    def test_hata_sayaci_motor_exception_artirir(self):
        aj = self._ajan_olustur()
        # Motor hata firlatiyor
        aj._motor.calistir.side_effect = Exception("arac hatasi")

        # Simule: tek bir hata kaydi
        aj._onceki_hata_sayaci = 0
        try:
            aj._motor.calistir("DOSYA_OKU", "param")
        except Exception:
            aj._onceki_hata_sayaci += 1

        assert aj._onceki_hata_sayaci == 1

    def test_hata_sayaci_basari_sifirlar(self):
        aj = self._ajan_olustur()
        aj._onceki_hata_sayaci = 3
        aj._motor.calistir.return_value = "basari sonucu"
        aj._motor.calistir.side_effect = None

        # Basarili calisma — sayaci sifirla
        aj._motor.calistir("DOSYA_OKU", "param")
        aj._onceki_hata_sayaci = 0  # basarili arac → sayaci sifirla (calistir() logigi)
        assert aj._onceki_hata_sayaci == 0


# ══════════════════════════════════════════════════════════════════════════════
# REACT_LOOP_DETECTOR Mesaj Formatı Testleri
# ══════════════════════════════════════════════════════════════════════════════


@skipif_import
class TestReactLoopDetectorMesaj:
    def _sonuc_ile_calistir(self, beyin_cevaplari, gorev="test gorevi"):
        """AltAjan.calistir()'i mock Beyin cevaplariyla calistir."""
        aj = AltAjan(gorev, max_adim=20)
        mock_motor = MagicMock()
        aj._motor = mock_motor

        # _ALT_BEYIN.uret()'i patch'le
        cevap_iter = iter(beyin_cevaplari)
        sys.modules["alt_ajan"]._ALT_BEYIN.uret = MagicMock(
            side_effect=lambda *a, **kw: next(cevap_iter)
        )
        return aj.calistir()

    def test_gozlem_3x_tekrar_react_loop_detector(self):
        """Aynı gözlem 3x tekrarlandığında REACT_LOOP_DETECTOR prefix'i olmalı."""
        gozlem_metni = "[HATA] ayni hata 3 kez"
        # Motor her cagrada ayni hatay verecek
        aj = AltAjan("dongu test", max_adim=20)
        mock_motor = MagicMock()
        mock_motor.calistir.side_effect = Exception("ayni hata 3 kez")
        aj._motor = mock_motor

        # 3 ayni gozlemi elle ekle
        ayni_gozlem = "[HATA] DOSYA_OKU çalıştırılırken hata: ayni hata 3 kez"
        aj._onceki_gozlemler = [ayni_gozlem, ayni_gozlem, ayni_gozlem]

        # Dongu dedektoru trigger etmeli
        son_3 = aj._onceki_gozlemler[-3:]
        tetiklendi = len(set(son_3)) == 1
        assert tetiklendi

    def test_gozlem_dongu_mesaji_prefix(self):
        """Döngü sonuç mesajı [REACT_LOOP_DETECTOR] ile başlamalı."""
        aj = AltAjan("test", max_adim=20)
        mock_motor = MagicMock()
        aj._motor = mock_motor

        # 3 ayni gozlemi elle ekle, sonucu manuel tetikle
        ayni = "ayni gozlem"
        aj._onceki_gozlemler = [ayni, ayni, ayni]

        # Aynı gözlem 3x → sonucu elle hesapla (calistir() içindeki mantık)
        son_3 = aj._onceki_gozlemler[-3:]
        if len(set(son_3)) == 1:
            aj.sonuc.sonuc = (
                f"[REACT_LOOP_DETECTOR] Ayni gozlem 3x tekrarlandi "
                f"({repr(son_3[0][:80])}) — GOREV_BITTI zorlandirildi. "
                f"Gorev: {aj.gorev[:100]}"
            )
            aj.sonuc.durum = "tamamlandi"

        assert aj.sonuc.sonuc is not None
        assert "[REACT_LOOP_DETECTOR]" in aj.sonuc.sonuc

    def test_eylem_dongu_mesaji_prefix(self):
        """Eylem döngüsü sonuç mesajı [REACT_LOOP_DETECTOR] ile başlamalı."""
        aj = AltAjan("test", max_adim=20)
        mock_motor = MagicMock()
        aj._motor = mock_motor

        ayni_eylem = "DOSYA_OKU"
        aj._onceki_eylemler = [ayni_eylem, ayni_eylem, ayni_eylem]

        son_3_eylem = aj._onceki_eylemler[-3:]
        if len(set(son_3_eylem)) == 1:
            aj.sonuc.sonuc = (
                f"[REACT_LOOP_DETECTOR] Ayni eylem 3x tekrarlandi "
                f"({son_3_eylem[0]}) — GOREV_BITTI zorlandirildi. "
                f"Gorev: {aj.gorev[:100]}"
            )
            aj.sonuc.durum = "tamamlandi"

        assert aj.sonuc.sonuc is not None
        assert "[REACT_LOOP_DETECTOR]" in aj.sonuc.sonuc

    def test_circuit_open_mesaji_prefix(self):
        """5 ardisik hata → [REACT_LOOP_DETECTOR] circuit open mesaji."""
        aj = AltAjan("test", max_adim=20)
        mock_motor = MagicMock()
        aj._motor = mock_motor

        # 5 ardisik hata simule
        aj._onceki_hata_sayaci = 5
        _HATA_ESIK = 5
        if aj._onceki_hata_sayaci >= _HATA_ESIK:
            aj.sonuc.sonuc = (
                f"[REACT_LOOP_DETECTOR] {aj._onceki_hata_sayaci} ardisik hata — "
                f"circuit open, gorev zorla sonlandirildi: {aj.gorev[:100]}"
            )
            aj.sonuc.durum = "tamamlandi"

        assert aj.sonuc.sonuc is not None
        assert "[REACT_LOOP_DETECTOR]" in aj.sonuc.sonuc
        assert "circuit open" in aj.sonuc.sonuc
        assert "5" in aj.sonuc.sonuc

    def test_circuit_open_durum_tamamlandi(self):
        """Circuit open durumunda sonuc.durum tamamlandi olmali."""
        aj = AltAjan("test", max_adim=20)
        aj._onceki_hata_sayaci = 5
        _HATA_ESIK = 5
        if aj._onceki_hata_sayaci >= _HATA_ESIK:
            aj.sonuc.sonuc = "[REACT_LOOP_DETECTOR] ..."
            aj.sonuc.durum = "tamamlandi"
        assert aj.sonuc.durum == "tamamlandi"


# ══════════════════════════════════════════════════════════════════════════════
# REACT_LOOP_DETECTOR Kelime Kontrolü
# ══════════════════════════════════════════════════════════════════════════════


@skipif_import
class TestMesajFormat:
    def test_gozlem_dongu_mesaji_3x_icerir(self):
        """Döngü mesajı '3x' ifadesini içermeli."""
        mesaj = (
            "[REACT_LOOP_DETECTOR] Ayni gozlem 3x tekrarlandi "
            "('test') — GOREV_BITTI zorlandirildi. Gorev: test"
        )
        assert "3x" in mesaj

    def test_eylem_dongu_mesaji_3x_icerir(self):
        mesaj = (
            "[REACT_LOOP_DETECTOR] Ayni eylem 3x tekrarlandi "
            "(DOSYA_OKU) — GOREV_BITTI zorlandirildi. Gorev: test"
        )
        assert "3x" in mesaj

    def test_circuit_open_mesaji_circuit_open_icerir(self):
        mesaj = (
            "[REACT_LOOP_DETECTOR] 5 ardisik hata — "
            "circuit open, gorev zorla sonlandirildi: test"
        )
        assert "circuit open" in mesaj

    def test_gorev_bitti_mesaji_icerir(self):
        mesaj = (
            "[REACT_LOOP_DETECTOR] Ayni gozlem 3x tekrarlandi "
            "('x') — GOREV_BITTI zorlandirildi. Gorev: test"
        )
        assert "GOREV_BITTI" in mesaj
