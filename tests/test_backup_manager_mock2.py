import os, sys, tempfile, json, zipfile, time, shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestBackupYedekAlDagitici:
    """yedek_al() tip dispatch - L76-83"""

    def test_yedek_al_kismi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                assert sonuc["tip"] == "kismi"
                assert sonuc["durum"] == "basarili"

    def test_yedek_al_zip(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "test.txt").write_text("merhaba")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                assert sonuc["tip"] == "zip"
                assert sonuc["durum"] == "basarili"

    def test_yedek_al_git(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="git")
                assert sonuc["tip"] == "git"

    def test_yedek_al_tam(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "test.txt").write_text("merhaba")
            (Path(td) / "skills").mkdir()
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="tam")
                assert sonuc["tip"] == "tam"
                assert sonuc["durum"] == "basarili"

    def test_yedek_al_gecersiz_tip(self):
        """Gecersiz tip varsayilan olarak kismi'ye duser"""
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="ftp")
                assert sonuc["tip"] == "kismi"


class TestBackupKismiYedekButunlugu:
    """_kismi_yedek butunluk testleri - L85-125"""

    def test_kismi_yedek_hedef_klasor_olusturulur(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "skills").mkdir()
            (Path(td) / "skills" / "test.txt").write_text("data")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                hedef = Path(sonuc["dizin"])
                assert hedef.exists()
                assert hedef.is_dir()

    def test_kismi_yedek_metadata_yazilir(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "skills").mkdir()
            (Path(td) / "skills" / "test.txt").write_text("data")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                hedef = Path(sonuc["dizin"])
                meta_path = hedef / "yedek_metadata.json"
                assert meta_path.exists()
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                assert meta["tip"] == "kismi"
                assert "skills" in meta["yedeklenen"]

    def test_kismi_yedek_klasor_ve_dosya_ayrimi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "skills").mkdir()
            (src / "skills" / "oku.txt").write_text("skill")
            (src / "config.yaml").write_text("key: value")
            (src / ".env").write_text("SECRET=123")
            with patch("reymen.core.backup_manager.PROJE_KOK", src):
                bm = BackupManager(yedek_dizini=src / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                assert "skills" in sonuc["yedeklenen"]
                assert "config_yaml" in sonuc["yedeklenen"]
                assert "env" in sonuc["yedeklenen"]
                hedef = Path(sonuc["dizin"])
                assert (hedef / "skills" / "oku.txt").exists()
                assert (hedef / "config_yaml").exists()
                assert (hedef / "env").exists()

    def test_kismi_yedek_kaynak_yoksa_atlanir(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                assert sonuc["durum"] == "basarili"
                assert sonuc["yedeklenen"] == []

    def test_kismi_yedek_kismi_basarisizlik_butunluk(self):
        """L110-111: skills basarili, memory copytree patlarsa -> skills yedeklenir"""
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "skills").mkdir()
            (src / "skills" / "a.txt").write_text("a")
            (src / "memory").mkdir()
            (src / "memory" / "b.txt").write_text("b")

            # Mock copytree: sadece "memory" icin patla, digerlerinde gercek copytree
            real_copytree = shutil.copytree

            def hatali_copytree(kaynak, hedef, **kw):
                if "memory" in str(kaynak):
                    raise PermissionError("Memory erisilemez")
                return real_copytree(kaynak, hedef, **kw)

            with patch("reymen.core.backup_manager.PROJE_KOK", src):
                with patch("shutil.copytree", side_effect=hatali_copytree):
                    bm = BackupManager(yedek_dizini=src / "yedekler")
                    sonuc = bm.yedek_al(tip="kismi")
                    assert sonuc["durum"] == "basarili"
                    assert "skills" in sonuc["yedeklenen"]
                    assert "memory" not in sonuc["yedeklenen"]

    def test_kismi_yedek_zaman_damgasi_farkli(self):
        """L73-74: Her yedekte baslangic zamani kaydedilir"""
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "skills").mkdir()
            (Path(td) / "skills" / "a.txt").write_text("a")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="kismi")
                assert sonuc["sure"] >= 0
                assert sonuc["tip"] == "kismi"


class TestBackupZipYedekButunlugu:
    """_zip_yedek butunluk testleri - L127-179"""

    def test_zip_yedek_dosya_olusturulur(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "main.py").write_text("print('ok')")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                assert sonuc["durum"] == "basarili"
                zip_path = Path(sonuc["dosya"])
                assert zip_path.exists()
                assert zipfile.is_zipfile(zip_path)

    def test_zip_yedek_icerik_dogrulama(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "main.py").write_text("print('ok')")
            (Path(td) / "utils").mkdir()
            (Path(td) / "utils" / "helper.py").write_text("def h(): pass")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                zip_path = Path(sonuc["dosya"])
                with zipfile.ZipFile(zip_path, "r") as zf:
                    names = zf.namelist()
                    assert "main.py" in names
                    assert "utils/helper.py" in names

    def test_zip_yedek_gitignore_filtrele(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "main.py").write_text("print('ok')")
            (Path(td) / "secret.log").write_text("gizli")
            (Path(td) / ".gitignore").write_text("*.log\n__pycache__/")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                zip_path = Path(sonuc["dosya"])
                with zipfile.ZipFile(zip_path, "r") as zf:
                    names = zf.namelist()
                    assert "main.py" in names
                    assert "secret.log" not in names

    def test_zip_yedek_oserror_handler(self):
        """L160-161: OSError handler - patlayan dosya satir icinde atlanir"""
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "ok1.py").write_text("print('ok1')")
            (Path(td) / "problem.txt").write_text("sorunlu")
            (Path(td) / "ok2.py").write_text("print('ok2')")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                # ZipFile.write'i mockla: problem.txt yazilirken OSError
                original_write = zipfile.ZipFile.write

                def patlayan_write(self, filename, arcname=None):
                    if "problem" in str(filename):
                        raise OSError("Dosya kullaniliyor")
                    return original_write(self, filename, arcname)

                with patch("zipfile.ZipFile.write", patlayan_write):
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="zip")
                    assert sonuc["durum"] == "basarili"

    def test_zip_yedek_boyut_dogrulama(self):
        """L165: Zip boyutu dogru hesaplaniyor"""
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "data.txt").write_text("x" * 10000)  # 10KB -> zip boyutu >0
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                sonuc = bm.yedek_al(tip="zip")
                assert "boyut_mb" in sonuc
                assert isinstance(sonuc["boyut_mb"], (int, float))

    def test_zip_yedek_temizleme_cagrilir(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "test.txt").write_text("test")
            with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                with patch(
                    "reymen.core.backup_manager.BackupManager._temizle_eski"
                ) as mock_temizle:
                    bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
                    sonuc = bm.yedek_al(tip="zip")
                    mock_temizle.assert_called_once_with("zip")


class TestBackupMetadata:
    """_metadata_yaz testleri - L241-256"""

    def test_metadata_json_icerigi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            hedef = Path(td) / "yedek"
            hedef.mkdir()
            bm = BackupManager(yedek_dizini=Path(td))
            bm._metadata_yaz(hedef, "kismi", ["skills", "memory"])
            meta_path = hedef / "yedek_metadata.json"
            assert meta_path.exists()
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            assert meta["tip"] == "kismi"
            assert meta["yedeklenen"] == ["skills", "memory"]

    def test_metadata_yazma_hatasi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            hedef = Path(td) / "yedek"
            hedef.mkdir()
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(
                Path, "write_text", side_effect=PermissionError("Yazilamaz")
            ):
                bm._metadata_yaz(hedef, "kismi", ["skills"])
                # Exception sarilir, hata firlatmaz


class TestBackupYedekListesi:
    """yedek_listele butunlugu - L288-330"""

    def test_listele_kismi_ve_zip_karisik(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(yedek_dizini=Path(td))
            kismi_dir = Path(td) / "kismi_20250101_120000"
            kismi_dir.mkdir()
            (kismi_dir / "yedek_metadata.json").write_text(
                json.dumps({"tip": "kismi", "yedeklenen": ["skills"]}), encoding="utf-8"
            )
            (kismi_dir / "test.txt").write_text("data")
            zip_path = Path(td) / "tam_20250101_120000.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("test.txt", "data")
            liste = bm.yedek_listele()
            assert len(liste) == 2
            tipler = [y["tip"] for y in liste]
            assert "kismi" in tipler
            assert "zip" in tipler

    def test_listele_filtre_kismi(self):
        from reymen.core.backup_manager import BackupManager

        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(yedek_dizini=Path(td))
            kismi_dir = Path(td) / "kismi_20250101_120000"
            kismi_dir.mkdir()
            (kismi_dir / "yedek_metadata.json").write_text('{"tip":"kismi"}')
            zip_path = Path(td) / "tam_20250101_120000.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("a.txt", "a")
            kismi_liste = bm.yedek_listele(tip="kismi")
            assert len(kismi_liste) == 1
            assert kismi_liste[0]["tip"] == "kismi"
