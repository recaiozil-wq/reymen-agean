"""Test: backup_manager kalan fonksiyonlar — git_yedek, motor_tools, geri_yukle butunlugu."""

from __future__ import annotations
import json, sys, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestGitYedek:
    """_git_yedek subprocess mock ile."""

    def test_git_yedek_basarili(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch("reymen.core.backup_manager.subprocess.run") as m:
                    m.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="git")
                    assert sonuc["durum"] in ("basarili", "kismi")
                    assert sonuc["tip"] == "git"

    def test_git_yedek_zaman_asimi(self):
        from reymen.core.backup_manager import BackupManager
        import subprocess

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch("reymen.core.backup_manager.subprocess.run") as m:
                    m.side_effect = subprocess.TimeoutExpired("cmd", 60)
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="git")
                    assert sonuc["durum"] in ("basarili", "kismi")
                    assert any(
                        "Zaman asimi" in str(a) for a in sonuc.get("adimlar", [])
                    )

    def test_git_yedek_genel_hata(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch("reymen.core.backup_manager.subprocess.run") as m:
                    m.side_effect = RuntimeError("Git calismiyor")
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="git")
                    assert sonuc["durum"] == "hata"


class TestMotorToolsKapsamli:
    """Motor tool fonksiyonlari _yedek_al_tool, _yedek_liste_tool, _geri_yukle_tool."""

    def test_yedek_al_tool_kismi(self):
        from reymen.core.backup_manager import _yedek_al_tool, BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch("reymen.core.backup_manager.backup_manager_al") as bm:
                    bm.return_value.yedek_al.return_value = {
                        "durum": "basarili",
                        "tip": "kismi",
                        "dizin": str(Path(td) / "yedek"),
                        "yedeklenen": ["skills"],
                        "sure": 0.5,
                    }
                    sonuc = _yedek_al_tool(tip="kismi")
                    assert "[YEDEK]" in sonuc
                    assert "Kismi" in sonuc

    def test_yedek_al_tool_zip(self):
        from reymen.core.backup_manager import _yedek_al_tool

        with patch("reymen.core.backup_manager.backup_manager_al") as bm:
            bm.return_value.yedek_al.return_value = {
                "durum": "basarili",
                "tip": "zip",
                "dosya": "/tmp/test.zip",
                "boyut_mb": 1.5,
                "sure": 2.0,
            }
            sonuc = _yedek_al_tool(tip="zip")
            assert "[YEDEK]" in sonuc
            assert "ZIP" in sonuc

    def test_yedek_al_tool_git(self):
        from reymen.core.backup_manager import _yedek_al_tool

        with patch("reymen.core.backup_manager.backup_manager_al") as bm:
            bm.return_value.yedek_al.return_value = {
                "durum": "basarili",
                "tip": "git",
                "hedef": "repo",
                "sure": 3.0,
            }
            sonuc = _yedek_al_tool(tip="git")
            assert "[YEDEK]" in sonuc

    def test_yedek_al_tool_tam(self):
        from reymen.core.backup_manager import _yedek_al_tool

        with patch("reymen.core.backup_manager.backup_manager_al") as bm:
            bm.return_value.yedek_al.return_value = {
                "durum": "basarili",
                "tip": "tam",
                "kismi": {"durum": "basarili"},
                "zip": {"durum": "basarili"},
                "sure": 5.0,
            }
            sonuc = _yedek_al_tool(tip="tam")
            assert "[YEDEK]" in sonuc
            assert "Tam" in sonuc

    def test_yedek_al_tool_hata(self):
        from reymen.core.backup_manager import _yedek_al_tool

        with patch("reymen.core.backup_manager.backup_manager_al") as bm:
            bm.return_value.yedek_al.return_value = {
                "durum": "hata",
                "hata": "Disk dolu",
            }
            sonuc = _yedek_al_tool(tip="kismi")
            assert "[HATA]" in sonuc

    def test_yedek_liste_tool_verili(self):
        from reymen.core.backup_manager import _yedek_liste_tool

        with patch("reymen.core.backup_manager.backup_manager_al") as bm:
            bm.return_value.yedek_listele.return_value = [
                {
                    "tip": "kismi",
                    "tarih": "2026-06-29T12:00:00",
                    "boyut": 1024,
                    "dizin": "/yedek/kismi_1",
                },
                {
                    "tip": "zip",
                    "tarih": "2026-06-29T13:00:00",
                    "boyut_mb": 5.2,
                    "dosya": "/yedek/tam_1.zip",
                },
            ]
            sonuc = _yedek_liste_tool()
            assert "Toplam" in sonuc
            assert "kismi" in sonuc.lower()
            assert "zip" in sonuc.lower()

    def test_geri_yukle_tool_basarili(self):
        from reymen.core.backup_manager import _geri_yukle_tool

        with patch("reymen.core.backup_manager.backup_manager_al") as bm:
            bm.return_value.geri_yukle.return_value = {
                "durum": "basarili",
                "kaynak": "/yedek",
                "geri_yuklenen": ["skills", "config"],
                "sure": 2.0,
            }
            sonuc = _geri_yukle_tool(kaynak="/yedek/kismi_1")
            assert "[GERI_YUKLE]" in sonuc

    def test_geri_yukle_tool_hata(self):
        from reymen.core.backup_manager import _geri_yukle_tool

        with patch("reymen.core.backup_manager.backup_manager_al") as bm:
            bm.return_value.geri_yukle.return_value = {
                "durum": "hata",
                "hata": "Kaynak bulunamadi",
            }
            sonuc = _geri_yukle_tool(kaynak="/olmayan")
            assert "[HATA]" in sonuc


class TestGeriYukleDetay:
    """Geri yukleme butunlugu testleri."""

    def test_geri_yukle_kismi_butun(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "skills").mkdir(parents=True)
            (Path(td) / "skills" / "f.txt").write_text("icerik")
            (Path(td) / "config.yaml").write_text("key: val")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                yedek = bm.yedek_al(tip="kismi")
                shutil_rm = __import__("shutil").rmtree
                shutil_rm(Path(td) / "skills")
                (Path(td) / "config.yaml").unlink()
                geri = bm.geri_yukle(yedek["dizin"])
                assert geri["durum"] == "basarili"
                assert "skills" in geri.get("geri_yuklenen", [])

    def test_geri_yukle_zip_cikti_dizini(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "test.txt").write_text("data")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                yedek = bm.yedek_al(tip="zip")
                geri = bm.geri_yukle(yedek["dosya"])
                assert geri["durum"] == "basarili"
                cikti = Path(geri["cikti"])
                assert cikti.exists()

    def test_geri_yukle_bilinmeyen_tip(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "unknown.xyz").write_text("x")
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            sonuc = bm.geri_yukle(str(Path(td) / "unknown.xyz"))
            assert sonuc["durum"] == "hata"

    def test_geri_yukle_exception(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            with patch.object(
                bm, "_kismi_geri_yukle", side_effect=RuntimeError("Kritik hata")
            ):
                sonuc = bm.geri_yukle(str(td))
                assert sonuc["durum"] == "hata"
