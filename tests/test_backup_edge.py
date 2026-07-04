"""Test: reymen/core/backup_manager.py — kalan sinir durumlari."""

from __future__ import annotations
import sys
import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestBackupSinirDurumlari:
    """Kalan sinir durumlari: tam yedek, dosya kopya hatasi, motor tools."""

    def test_tam_yedek_calisir(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "skills").mkdir(parents=True)
            (Path(td) / "skills" / "f.txt").write_text("x")
            (Path(td) / "test.txt").write_text("test")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="tam")
                assert sonuc["durum"] == "basarili"
                assert sonuc["kismi"]["durum"] == "basarili"
                assert sonuc["zip"]["durum"] == "basarili"

    def test_kismi_yedek_copy2_hatasi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "config.yaml").write_text("key: val")
            (Path(td) / "skills").mkdir(parents=True)
            (Path(td) / "skills" / "f.txt").write_text("x")
            orig_copy2 = shutil.copy2

            def broken_copy2(src, dst, **kw):
                if "config" in str(src) or "yaml" in str(src):
                    raise PermissionError("Engellendi!")
                return orig_copy2(src, dst, **kw)

            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch("reymen.core.backup_manager.shutil.copy2", broken_copy2):
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="kismi")
                    assert sonuc["durum"] == "basarili"
                    assert "skills" in sonuc["yedeklenen"]

    def test_yedek_al_gecersiz_tip(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="gecersiz")
                assert sonuc["durum"] == "basarili"

    def test_durum_raporu(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                d = bm.durum()
                assert "yedek_dizini" in d
                assert "toplam_yedek" in d
                assert "max_yedek" in d

    def test_singleton(self):
        from reymen.core.backup_manager import backup_manager_al

        with patch("reymen.core.backup_manager.PROJE_KOK", Path(tempfile.mkdtemp())):
            b1 = backup_manager_al()
            b2 = backup_manager_al()
            assert b1 is b2

    def test_motor_kaydet(self):
        from reymen.core.backup_manager import motor_kaydet

        class Motor:
            def _plugin_arac_kaydet(self, ad, func, desc=""):
                self.tools[ad] = (func, desc)

        m = Motor()
        m.tools = {}
        motor_kaydet(m)
        assert "YEDEK_AL" in m.tools
        assert "YEDEK_LISTE" in m.tools
        assert "GERI_YUKLE" in m.tools

    def test_motor_yedek_al_tool_gecersiz(self):
        from reymen.core.backup_manager import _yedek_al_tool

        sonuc = _yedek_al_tool(tip="bilinmeyen")
        assert "[HATA]" in sonuc

    def test_motor_yedek_liste_tool_bos(self):
        from reymen.core.backup_manager import _yedek_liste_tool

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch("reymen.core.backup_manager.backup_manager_al") as mock_bm:
                    mock_bm.return_value.yedek_listele.return_value = []
                    sonuc = _yedek_liste_tool()
                    assert "Henuz yedek" in sonuc

    def test_motor_geri_yukle_tool_paramsiz(self):
        from reymen.core.backup_manager import _geri_yukle_tool

        sonuc = _geri_yukle_tool()
        assert "[HATA]" in sonuc
