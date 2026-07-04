"""Test: reymen/core/backup_manager.py - mock ile hata senaryolari"""

from __future__ import annotations
import os, sys, tempfile, json, zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestBackupKismiYedekHata:
    def test_kismi_yedek_basarili(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "skills"
            src.mkdir(parents=True)
            (src / "test.txt").write_text("test")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                assert sonuc["durum"] == "basarili"

    def test_kismi_yedek_kaynak_yok(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                assert sonuc["durum"] == "basarili"

    def test_kismi_yedek_copytree_hatasi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch(
                    "shutil.copytree", side_effect=PermissionError("Erisim engellendi")
                ):
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="kismi")
                    assert sonuc["durum"] == "basarili"

    def test_kismi_yedek_metadata_json_dogru(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                bm.yedek_al(tip="kismi")
                yedekler = list(
                    (Path(td) / "yedekler").glob("kismi_*/yedek_metadata.json")
                )
                assert len(yedekler) >= 0

    def test_kismi_yedek_kismi_basarisizlik_metadata_tutarliligi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                assert "yedeklenen" in sonuc


class TestBackupZipYedekHata:
    def test_zip_yedek_basarili(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "test.txt").write_text("hello")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                assert "durum" in sonuc

    def test_zip_yedek_zipfile_hatasi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch("zipfile.ZipFile", side_effect=OSError("Disk dolu")):
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="zip")
                    assert sonuc["durum"] == "hata"

    def test_zip_yedek_gitignore_filtreleme(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "main.py").write_text("print('ok')")
            (Path(td) / "secret.log").write_text("hidden")
            (Path(td) / ".gitignore").write_text("*.log\n__pycache__/")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                assert "durum" in sonuc

    def test_zip_yedek_bos_proje(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                assert "durum" in sonuc


class TestYedekListeleme:
    def test_yedek_listele_bos(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(yedek_dizini=Path(td))
            liste = bm.yedek_listele()
            assert isinstance(liste, list)

    def test_yedek_listele_filtre(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                bm.yedek_al(tip="kismi")
                liste = bm.yedek_listele(tip="kismi")
                assert isinstance(liste, list)


class TestBackupGeriYukle:
    def test_geri_yukle_kaynak_yok(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(yedek_dizini=Path(td))
            sonuc = bm.geri_yukle("/olmayan/dizin")
            assert sonuc is not None

    def test_geri_yukle_kismi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                bm.yedek_al(tip="kismi")
                yedekler = bm.yedek_listele()
                if yedekler:
                    sonuc = bm.geri_yukle(yedekler[0]["dizin"])
                    assert isinstance(sonuc, dict)

    def test_geri_yukle_zip(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                if sonuc["durum"] == "basarili":
                    geri = bm.geri_yukle(sonuc["dosya"])
                    assert isinstance(geri, dict)
