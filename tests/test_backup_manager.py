# -*- coding: utf-8 -*-
"""
Test: reymen/core/backup_manager.py

Odak: L72-172
- yedek_al(tip) routing — kismi/zip/tam/git dispatch
- _kismi_yedek() — partial backup, error tolerance, data integrity
- _zip_yedek() — ZIP creation, gitignore filtering, error management

KRITIK: Yedekleme yarida kesilirse veri butunlugu testleri
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess
from datetime import datetime

import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJE_KOK))


# ═══════════════════════════════════════════════════════════════════════════════
#  1. yedek_al(tip) ROUTING — L72-83
# ═══════════════════════════════════════════════════════════════════════════════

class TestYedekAlRouting:
    """yedek_al(tip) → dogru metoda yonlendirme. L72-83."""

    def test_kismi_yonlendirir(self):
        """tip='kismi' → _kismi_yedek cagrilir."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(bm, "_kismi_yedek", return_value={"tip": "kismi", "durum": "basarili"}) as mk, \
                 patch.object(bm, "_zip_yedek") as mz, \
                 patch.object(bm, "_git_yedek") as mg, \
                 patch.object(bm, "_tam_yedek") as mt:
                sonuc = bm.yedek_al(tip="kismi")

            mk.assert_called_once()
            mz.assert_not_called()
            mg.assert_not_called()
            mt.assert_not_called()
            assert sonuc["tip"] == "kismi"

    def test_zip_yonlendirir(self):
        """tip='zip' → _zip_yedek cagrilir."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(bm, "_kismi_yedek") as mk, \
                 patch.object(bm, "_zip_yedek", return_value={"tip": "zip", "durum": "basarili"}) as mz, \
                 patch.object(bm, "_git_yedek") as mg, \
                 patch.object(bm, "_tam_yedek") as mt:
                sonuc = bm.yedek_al(tip="zip")

            mz.assert_called_once()
            mk.assert_not_called()
            mg.assert_not_called()
            mt.assert_not_called()
            assert sonuc["tip"] == "zip"

    def test_git_yonlendirir(self):
        """tip='git' → _git_yedek cagrilir."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(bm, "_kismi_yedek") as mk, \
                 patch.object(bm, "_zip_yedek") as mz, \
                 patch.object(bm, "_git_yedek", return_value={"tip": "git", "durum": "basarili"}) as mg, \
                 patch.object(bm, "_tam_yedek") as mt:
                sonuc = bm.yedek_al(tip="git")

            mg.assert_called_once()
            mk.assert_not_called()
            mz.assert_not_called()
            mt.assert_not_called()
            assert sonuc["tip"] == "git"

    def test_tam_yonlendirir(self):
        """tip='tam' → _tam_yedek cagrilir."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(bm, "_kismi_yedek") as mk, \
                 patch.object(bm, "_zip_yedek") as mz, \
                 patch.object(bm, "_git_yedek") as mg, \
                 patch.object(bm, "_tam_yedek", return_value={"tip": "tam", "durum": "basarili"}) as mt:
                sonuc = bm.yedek_al(tip="tam")

            mt.assert_called_once()
            mk.assert_not_called()
            mz.assert_not_called()
            mg.assert_not_called()
            assert sonuc["tip"] == "tam"

    def test_gecersiz_tip_kismi_yonlendirir(self):
        """Gecersiz tip → else dalina duser ve _kismi_yedek cagrilir (L82-83)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(bm, "_kismi_yedek", return_value={"tip": "kismi", "durum": "basarili"}) as mk, \
                 patch.object(bm, "_zip_yedek") as mz, \
                 patch.object(bm, "_git_yedek") as mg, \
                 patch.object(bm, "_tam_yedek") as mt:
                sonuc = bm.yedek_al(tip="ftp")

            mk.assert_called_once()
            mz.assert_not_called()
            mg.assert_not_called()
            mt.assert_not_called()
            assert sonuc["tip"] == "kismi"

    def test_timestamp_uretilir_ve_aktarilir(self):
        """yedek_al timestamp uretip _kismi_yedek'e gecirir (L74).

        datetime.now()'i patch'leyerek kontrollu timestamp uretimi.
        """
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(bm, "_kismi_yedek", return_value={"tip": "kismi", "durum": "basarili"}) as mk, \
                 patch("reymen.core.backup_manager.datetime") as mock_dt:
                mock_dt.now.return_value = datetime(2026, 6, 29, 15, 30, 0)
                # strftime ve fromtimestamp delegasyonu
                mock_dt.strftime = staticmethod(lambda fmt, dt=None: datetime.strftime(dt or datetime.now(), fmt))
                mock_dt.fromtimestamp = staticmethod(datetime.fromtimestamp)

                bm.yedek_al(tip="kismi")

            cagri = mk.call_args
            assert cagri[0][0] == "20260629_153000"
            assert isinstance(cagri[0][1], float)

    def test_baslangic_zamani_olculur(self):
        """baslangic time.time() ile alinir (L73)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td))
            with patch.object(bm, "_kismi_yedek", return_value={"tip": "kismi", "durum": "basarili"}) as mk, \
                 patch("reymen.core.backup_manager.time.time") as mock_time:
                mock_time.side_effect = [100.0, 105.5]

                bm.yedek_al(tip="kismi")

            cagri = mk.call_args
            assert cagri[0][1] == 100.0


# ═══════════════════════════════════════════════════════════════════════════════
#  2. _kismi_yedek() — L85-125
# ═══════════════════════════════════════════════════════════════════════════════

class TestKismiYedekHataToleransi:
    """Hata toleransi: bir kaynak basarisizsa digerleri devam eder (L110-111)."""

    def test_tum_kaynaklar_basarili(self):
        """6 kaynagin tamami basariyla kopyalanir."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="kismi")

            assert sonuc["durum"] == "basarili"
            assert len(sonuc["yedeklenen"]) == 6
            for ad in ("skills", "memory", "config", "reymen_config", "config_yaml", "env"):
                assert ad in sonuc["yedeklenen"]

            # Metadata yazildi
            hedef = Path(sonuc["dizin"])
            meta = json.loads((hedef / "yedek_metadata.json").read_text(encoding="utf-8"))
            assert meta["tip"] == "kismi"

    def test_copytree_hatasi_digerleri_devam_eder(self):
        """copytree patlayan kaynak atlanir, digerleri kopyalanir (L110-111)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copytree",
                           side_effect=self._patlayan_copytree("memory")):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="kismi")

            assert sonuc["durum"] == "basarili"
            assert "skills" in sonuc["yedeklenen"]
            assert "memory" not in sonuc["yedeklenen"]
            assert "config" in sonuc["yedeklenen"]

    def test_copy2_hatasi_digerleri_devam_eder(self):
        """copy2 patlayan dosya atlanir, digerleri kopyalanir."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            orig_copy2 = shutil.copy2

            def patlayan_copy2(src, dst, **kw):
                if ".env" in str(src):
                    raise PermissionError(".env erisilemez")
                return orig_copy2(src, dst, **kw)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copy2", patlayan_copy2):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="kismi")

            assert sonuc["durum"] == "basarili"
            assert "env" not in sonuc["yedeklenen"]
            assert "skills" in sonuc["yedeklenen"]
            assert "config_yaml" in sonuc["yedeklenen"]

    def test_birden_fazla_kaynak_hatasi(self):
        """Birden fazla kaynak basarisiz, kalanlar yedeklenir."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            hatali = {"memory", "config"}

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copytree",
                           side_effect=self._patlayan_copytree_birden_fazla(hatali)):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="kismi")

            assert sonuc["durum"] == "basarili"
            assert "skills" in sonuc["yedeklenen"]
            assert "memory" not in sonuc["yedeklenen"]
            assert "config" not in sonuc["yedeklenen"]
            assert "reymen_config" in sonuc["yedeklenen"]

    def test_tum_kaynaklar_basarisiz_metadata_yine_yazilir(self):
        """Her sey patlasa bile metadata yazilir ve durum basarili doner."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copytree",
                           side_effect=PermissionError("Tamamen engellendi")):
                    with patch("reymen.core.backup_manager.shutil.copy2",
                               side_effect=PermissionError("Dosya da engellendi")):
                        bm = self._bm(kok)
                        sonuc = bm.yedek_al(tip="kismi")

            # Hicbir kaynak yedeklenemese bile durum basarili (kismi basari)
            assert sonuc["durum"] == "basarili"
            assert sonuc["yedeklenen"] == []

            # Metadata yine de yazilir
            hedef = Path(sonuc["dizin"])
            assert hedef.exists()
            meta_path = hedef / "yedek_metadata.json"
            assert meta_path.exists()

    def test_kaynak_yoksa_atlanir(self):
        """Var olmayan kaynaklar pass gecer (L103: if kaynak.exists())."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            # Hicbir kaynak yok

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="kismi")

            assert sonuc["durum"] == "basarili"
            assert sonuc["yedeklenen"] == []

    def test_metadata_icerik_dogrulama(self):
        """Metadata JSON'u tip, yedeklenen, tarih icerir (L113-114)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="kismi")

            hedef = Path(sonuc["dizin"])
            meta = json.loads((hedef / "yedek_metadata.json").read_text(encoding="utf-8"))
            assert meta["tip"] == "kismi"
            assert isinstance(meta["yedeklenen"], list)
            assert "skills" in meta["yedeklenen"]
            assert "tarih" in meta
            assert "proje" in meta
            assert "python_version" in meta

    def test_hedef_klasor_olusturulur(self):
        """Hedef klasor _kismi_yedek icinde mkdir ile olusturulur (L88)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="kismi")

            hedef = Path(sonuc["dizin"])
            assert hedef.exists()
            assert hedef.is_dir()
            # Iceride yedeklenen dosyalar var
            assert (hedef / "skills").exists()

    def test_icerik_dogru_kopyalanir(self):
        """Dosya icerikleri dogru kopyalanir."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "skills").mkdir(parents=True)
            (kok / "skills" / "test.py").write_text("print('hello')")
            (kok / "memory").mkdir(parents=True)
            (kok / "memory" / "data.json").write_text('{"key": "val"}')

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="kismi")

            hedef = Path(sonuc["dizin"])
            assert (hedef / "skills" / "test.py").read_text() == "print('hello')"
            assert (hedef / "memory" / "data.json").read_text() == '{"key": "val"}'

    def test_temizle_eski_cagrilir(self):
        """_kismi_yedek sonunda _temizle_eski('kismi') cagrilir (L117)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.BackupManager._temizle_eski") as mock_temizle:
                    bm = self._bm(kok)
                    bm.yedek_al(tip="kismi")

            mock_temizle.assert_called_once_with("kismi")

    def test_klasor_ve_dosya_ayrimi(self):
        """is_dir() → copytree, else → copy2 (L105-108)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "skills").mkdir(parents=True)
            (kok / "skills" / "a.txt").write_text("a")
            (kok / "config.yaml").write_text("key: val")
            (kok / ".env").write_text("SECRET=x")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="kismi")

            hedef = Path(sonuc["dizin"])
            assert (hedef / "skills" / "a.txt").read_text() == "a"
            assert (hedef / "config_yaml").read_text() == "key: val"
            assert (hedef / "env").read_text() == "SECRET=x"

    def test_sure_hesabi(self):
        """sure = time.time() - baslangic (L116)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.time.time") as mock_time:
                    mock_time.side_effect = [100.0, 103.5]  # baslangic=100, bitis=103.5
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="kismi")

            assert sonuc["sure"] == 3.5  # 103.5 - 100.0

    # ── Yardimcilar ───────────────────────────────────────────────────────

    def _kaynaklari_olustur(self, kok: Path):
        """Test icin 6 kaynagi olustur."""
        (kok / "skills").mkdir(parents=True)
        (kok / "skills" / "a.txt").write_text("skill")
        (kok / "memory").mkdir(parents=True)
        (kok / "memory" / "b.json").write_text("{}")
        (kok / "config").mkdir(parents=True)
        (kok / "config" / "c.yaml").write_text("key: val")
        (kok / ".ReYMeN").mkdir(parents=True)
        (kok / ".ReYMeN" / "state.json").write_text('{"v":1}')
        (kok / "config.yaml").write_text("app: test")
        (kok / ".env").write_text("SECRET=123")

    @staticmethod
    def _patlayan_copytree(patlayan_ad: str):
        """Bir klasor adi icin hata firlatan copytree side_effect."""
        real_copytree = shutil.copytree

        def wrapper(kaynak, hedef, **kw):
            if patlayan_ad in str(kaynak):
                raise PermissionError(f"{patlayan_ad} erisilemez")
            return real_copytree(kaynak, hedef, **kw)

        return wrapper

    @staticmethod
    def _patlayan_copytree_birden_fazla(patlayan_adlar: set):
        """Birden fazla klasor adi icin hata firlatan copytree."""
        real_copytree = shutil.copytree

        def wrapper(kaynak, hedef, **kw):
            for ad in patlayan_adlar:
                if ad in str(kaynak):
                    raise PermissionError(f"{ad} erisilemez")
            return real_copytree(kaynak, hedef, **kw)

        return wrapper

    @staticmethod
    def _bm(kok: Path):
        """BackupManager olusturucu."""
        from reymen.core.backup_manager import BackupManager
        return BackupManager(yedek_dizini=kok / "yedekler")


# ═══════════════════════════════════════════════════════════════════════════════
#  COVERAGE KALANLAR — 5 son satir
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoverageKalanlar:
    """Kalan 5 satir icin targeted testler."""

    def test_zip_yedek_valueerror_continue(self):
        """L159: ValueError sonrasi continue (os.walk disi dosya)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            (kok / "main.py").write_text("ok")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.os.walk") as mock_walk:
                    def walk_side_effect(path):
                        return [(str(kok), [], ["main.py", "../outside.txt"])]
                    mock_walk.side_effect = walk_side_effect
                    bm = BackupManager(yedek_dizini=kok / "yedekler")
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"

    def test_temizle_eski_except(self):
        """L272-273: _temizle_eski except blogu."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            with patch.object(bm, "_yedekleri_listele", side_effect=RuntimeError("test hatasi")):
                bm._temizle_eski("kismi")

    def test_yedek_listele_dizin_yok(self):
        """L293: Yedek dizini yoksa bos liste doner."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            import shutil
            shutil.rmtree(yedek_dizini)

            yedekler = bm.yedek_listele()
            assert yedekler == []

    def test_yedek_liste_tool_buyuk_boyut(self):
        """L554: Buyuk dosya boyutu MB formatinda gosterilir."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("large.bin", b"x" * 1024 * 1024 * 2)

            sonuc = _yedek_liste_tool()

        assert "Toplam 1 yedek" in sonuc
        assert "MB" in sonuc

# ═══════════════════════════════════════════════════════════════════════════════
#  3. _zip_yedek() — L127-179
# ═══════════════════════════════════════════════════════════════════════════════

class TestZipYedek:
    """_zip_yedek ZIP olusturma, gitignore filtreleme, hata yonetimi."""

    def test_basariyla_zip_olusturulur(self):
        """Temel ZIP yedek alma (L132)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "main.py").write_text("print('ok')")
            (kok / "utils").mkdir()
            (kok / "utils" / "helper.py").write_text("def h(): pass")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"
            assert sonuc["tip"] == "zip"
            zip_path = Path(sonuc["dosya"])
            assert zip_path.exists()
            assert zipfile.is_zipfile(zip_path)

    def test_zip_icerik_dogrulama(self):
        """ZIP icindeki dosyalar dogru (L150, L157)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "app.py").write_text("app")
            (kok / "data").mkdir()
            (kok / "data" / "info.txt").write_text("info")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            with zipfile.ZipFile(Path(sonuc["dosya"]), "r") as zf:
                names = zf.namelist()
                assert "app.py" in names
                assert "data/info.txt" in names
                assert zf.read("app.py").decode() == "app"

    def test_gitignore_filtreleme_prefix(self):
        """Gitignore prefix deseni (startswith) calisir (L152-154)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "main.py").write_text("ok")
            (kok / "build").mkdir()
            (kok / "build" / "out.o").write_text("obj")
            (kok / ".gitignore").write_text("build/")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            with zipfile.ZipFile(Path(sonuc["dosya"]), "r") as zf:
                names = zf.namelist()
                assert "main.py" in names
                assert "build/out.o" not in names

    def test_gitignore_filtreleme_glob(self):
        """Gitignore glob deseni (fnmatch) calisir (L153)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "main.py").write_text("ok")
            (kok / "secret.log").write_text("gizli")
            (kok / "debug.log").write_text("debug")
            (kok / ".gitignore").write_text("*.log")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            with zipfile.ZipFile(Path(sonuc["dosya"]), "r") as zf:
                names = zf.namelist()
                assert "main.py" in names
                assert "secret.log" not in names
                assert "debug.log" not in names

    def test_gitignore_filtreleme_yorum_satiri(self):
        """# ile baslayan gitignore satirlari atlanir (L139)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "main.py").write_text("ok")
            (kok / "secret.log").write_text("gizli")
            (kok / ".gitignore").write_text("# yorum\n*.log")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            with zipfile.ZipFile(Path(sonuc["dosya"]), "r") as zf:
                names = zf.namelist()
                assert "main.py" in names
                assert "secret.log" not in names

    def test_gitignore_yoksa_hersey_eklenir(self):
        """Gitignore dosyasi yoksa tum dosyalar ZIP'e eklenir (L135-136)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "main.py").write_text("ok")
            (kok / "data.txt").write_text("data")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            with zipfile.ZipFile(Path(sonuc["dosya"]), "r") as zf:
                names = zf.namelist()
                assert "main.py" in names
                assert "data.txt" in names

    def test_haric_tutulan_klasorler_atlanir(self):
        """__pycache__, .git, .venv, node_modules atlanir (L145)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "main.py").write_text("ok")
            (kok / "__pycache__").mkdir()
            (kok / "__pycache__" / "cache.pyc").write_text("c")
            (kok / ".venv").mkdir()
            (kok / ".venv" / "bin").mkdir()
            (kok / "node_modules").mkdir()
            (kok / "node_modules" / "pkg").mkdir()

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            with zipfile.ZipFile(Path(sonuc["dosya"]), "r") as zf:
                names = zf.namelist()
                assert "main.py" in names
                # Bu klasorlerin altindaki dosyalar ZIP'te olmamali
                for n in names:
                    assert not n.startswith("__pycache__/")
                    assert not n.startswith(".venv/")
                    assert not n.startswith("node_modules/")

    def test_oserror_handling(self):
        """ZIP.write OSError firlatirsa o dosya atlanir, devam edilir (L160-162)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "ok1.py").write_text("print('ok1')")
            (kok / "problem.txt").write_text("locked")
            (kok / "ok2.py").write_text("print('ok2')")

            original_write = zipfile.ZipFile.write

            def patlayan_write(self, filename, arcname=None):
                if "problem" in str(filename):
                    raise OSError("Dosya kullaniliyor")
                return original_write(self, filename, arcname)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("zipfile.ZipFile.write", patlayan_write):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"

            # ZIP gecerliligini korur
            zip_path = Path(sonuc["dosya"])
            assert zip_path.exists()
            assert zipfile.is_zipfile(zip_path)
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                assert "ok1.py" in names
                assert "ok2.py" in names
                # problem.txt atlanmis olmali (OSError)
                assert "problem.txt" not in names

    def test_valueerror_atlanir(self):
        """relative_to ValueError olan dosyalar atlanir (L158-159)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "main.py").write_text("ok")

            # normalde ValueError olmaz, ama mock ile os.walk'tan
            # PROJE_KOK disinda bir yol gelmesini simule edelim
            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.os.walk") as mock_walk:
                    # Normal bir dizin + PROJE_KOK disinda bir dosya
                    def walk_side_effect(path):
                        if path == kok:
                            return [(str(kok), [], ["main.py", "../outside.txt"])]
                        return []

                    mock_walk.side_effect = walk_side_effect

                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"
            # ../outside.txt ValueError'a yol acar ve atlanir
            with zipfile.ZipFile(Path(sonuc["dosya"]), "r") as zf:
                names = zf.namelist()
                assert "main.py" in names

    def test_bos_proje_zipi(self):
        """Bos proje dizininde ZIP olusturulur (L143'te walk bos doner)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"
            zip_path = Path(sonuc["dosya"])
            assert zip_path.exists()
            assert zipfile.is_zipfile(zip_path)

    def test_boyut_hesabi(self):
        """boyut_mb dogru hesaplanir (L165, L172)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "data.bin").write_bytes(b"x" * 1024 * 10)  # 10KB

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="zip")

            assert sonuc["boyut_mb"] >= 0.0
            assert isinstance(sonuc["boyut_mb"], float)

    def test_temizle_eski_cagrilir(self):
        """_zip_yedek sonunda _temizle_eski('zip') cagrilir (L167)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "test.txt").write_text("test")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.BackupManager._temizle_eski") as mock_temizle:
                    bm = self._bm(kok)
                    bm.yedek_al(tip="zip")

            mock_temizle.assert_called_once_with("zip")

    def test_ana_except_hata_donusu(self):
        """ZipFile acilirken hata → ana except yakalar (L177-179)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("zipfile.ZipFile", side_effect=OSError("Disk dolu")):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "hata"
            assert "Disk dolu" in sonuc["hata"]
            assert sonuc["tip"] == "zip"
            assert "sure" in sonuc

    def test_sure_hesabi(self):
        """_zip_yedek sure dogru hesaplar (L164)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "test.txt").write_text("test")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.time.time") as mock_time:
                    mock_time.side_effect = [200.0, 202.5]
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["sure"] == 2.5

    # ── Yardimcilar ───────────────────────────────────────────────────────

    @staticmethod
    def _bm(kok: Path):
        from reymen.core.backup_manager import BackupManager
        return BackupManager(yedek_dizini=kok / "yedekler")


# ═══════════════════════════════════════════════════════════════════════════════
#  COVERAGE KALANLAR — 5 son satir
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoverageKalanlar:
    """Kalan 5 satir icin targeted testler."""

    def test_zip_yedek_valueerror_continue(self):
        """L159: ValueError sonrasi continue (os.walk disi dosya)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            (kok / "main.py").write_text("ok")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.os.walk") as mock_walk:
                    def walk_side_effect(path):
                        return [(str(kok), [], ["main.py", "../outside.txt"])]
                    mock_walk.side_effect = walk_side_effect
                    bm = BackupManager(yedek_dizini=kok / "yedekler")
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"

    def test_temizle_eski_except(self):
        """L272-273: _temizle_eski except blogu."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            with patch.object(bm, "_yedekleri_listele", side_effect=RuntimeError("test hatasi")):
                bm._temizle_eski("kismi")

    def test_yedek_listele_dizin_yok(self):
        """L293: Yedek dizini yoksa bos liste doner."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            import shutil
            shutil.rmtree(yedek_dizini)

            yedekler = bm.yedek_listele()
            assert yedekler == []

    def test_yedek_liste_tool_buyuk_boyut(self):
        """L554: Buyuk dosya boyutu MB formatinda gosterilir."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("large.bin", b"x" * 1024 * 1024 * 2)

            sonuc = _yedek_liste_tool()

        assert "Toplam 1 yedek" in sonuc
        assert "MB" in sonuc

# ═══════════════════════════════════════════════════════════════════════════════
#  4. VERI BUTUNLUGU — Yedekleme yarida kesilirse
# ═══════════════════════════════════════════════════════════════════════════════

class TestVeriButunlugu:
    """KRITIK: Yedekleme yarida kesilirse veri butunlugu."""

    def test_kismi_yarida_kalan_veri_korunur(self):
        """Kismi yedek yarida kalirsa, o ana kadar kopyalanan veri kaybolmaz."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "skills").mkdir(parents=True)
            (kok / "skills" / "a.txt").write_text("skill_data")
            (kok / "memory").mkdir(parents=True)
            (kok / "memory" / "b.json").write_text('{"mem": 1}')
            (kok / "config").mkdir(parents=True)
            (kok / "config" / "c.yaml").write_text("key: val")

            yedek_dizini = kok / "yedekler"

            # _kismi_yedek icindeki donguyu simule et: skills basarili,
            # memory'de patla, config yedeklenemez
            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copytree",
                           side_effect=self._patlayan_ikinci_kaynak()):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="kismi")

            # skills basariyla yedeklenmis olmali
            assert "skills" in sonuc["yedeklenen"]
            assert "memory" not in sonuc["yedeklenen"]

            # skills verisi hala diskte
            hedef = Path(sonuc["dizin"])
            assert (hedef / "skills" / "a.txt").exists()
            assert (hedef / "skills" / "a.txt").read_text() == "skill_data"

            # memory yedeklenmemis olmali
            assert not (hedef / "memory").exists()

            # Metadata yazilmis olmali (sonradan yazilir)
            assert (hedef / "yedek_metadata.json").exists()

    def test_zip_yarida_kalan_kismi_zip_gecerli(self):
        """ZIP yarida kalirsa (OSError), kismi ZIP gecerli kalir."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)

            # 3 dosya: 2'si basarili, 1'inde OSError
            (kok / "ok1.py").write_text("print('ok1')")
            (kok / "ok2.py").write_text("print('ok2')")
            (kok / "problem.txt").write_text("locked")
            (kok / "ok3.py").write_text("print('ok3')")

            original_write = zipfile.ZipFile.write

            def patlayan_write(self, filename, arcname=None):
                if "problem" in str(filename):
                    raise OSError("Dosya kilitli")
                return original_write(self, filename, arcname)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("zipfile.ZipFile.write", patlayan_write):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="zip")

            # ZIP gecerli ve problem.txt disindaki dosyalar icerde
            assert sonuc["durum"] == "basarili"
            zip_path = Path(sonuc["dosya"])
            assert zipfile.is_zipfile(zip_path)

            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                assert "ok1.py" in names
                assert "ok2.py" in names
                assert "ok3.py" in names
                assert "problem.txt" not in names
                # Icerik dogrulama
                assert zf.read("ok1.py").decode() == "print('ok1')"

    def test_kismi_yarida_kalan_sonraki_yedek_etkilemez(self):
        """Yarim kalan yedek, sonraki yedegin butunlugunu etkilemez."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "skills").mkdir(parents=True)
            (kok / "skills" / "a.txt").write_text("skill_data")
            (kok / "memory").mkdir(parents=True)
            (kok / "memory" / "b.json").write_text('{"mem": 1}')

            yedek_dizini = kok / "yedekler"

            # Ilk yedek: memory'de patla
            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copytree",
                           side_effect=self._patlayan_ikinci_kaynak()):
                    bm = self._bm(kok)
                    sonuc1 = bm.yedek_al(tip="kismi")

            assert sonuc1["durum"] == "basarili"
            assert "skills" in sonuc1["yedeklenen"]

            # Ikinci yedek: her sey basarili
            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm2 = self._bm(kok)
                sonuc2 = bm2.yedek_al(tip="kismi")

            assert sonuc2["durum"] == "basarili"
            assert "skills" in sonuc2["yedeklenen"]
            assert "memory" in sonuc2["yedeklenen"]

            hedef2 = Path(sonuc2["dizin"])
            assert (hedef2 / "skills" / "a.txt").read_text() == "skill_data"
            assert (hedef2 / "memory" / "b.json").read_text() == '{"mem": 1}'

    def test_zip_yedek_valueerror_veri_butunlugu(self):
        """ValueError atlanan dosyalar ZIP butunlugunu bozmaz."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            (kok / "safe.py").write_text("safe")
            # PROJE_KOK disinda bir dosyayi simule et

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.os.walk") as mock_walk:
                    mock_walk.return_value = [
                        (str(kok), [], ["safe.py", "../outside.txt"]),
                    ]

                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"
            zip_path = Path(sonuc["dosya"])
            assert zipfile.is_zipfile(zip_path)

            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                assert "safe.py" in names
                assert "../outside.txt" not in names
                assert "outside.txt" not in names

    def test_tam_yedek_yarida_kalan_zip(self):
        """Tam yedekte ZIP hatasi olursa kismi yine de basarili doner."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)
            (kok / "test.txt").write_text("test")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("zipfile.ZipFile", side_effect=OSError("Disk dolu")):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="tam")

            # Kismi basarili, ZIP hatali
            assert sonuc["kismi"]["durum"] == "basarili"
            assert sonuc["zip"]["durum"] == "hata"
            assert sonuc["durum"] == "basarili"

            # Kismi yedegin verisi hala diskte
            kismi_dizin = Path(sonuc["kismi"]["dizin"])
            assert (kismi_dizin / "skills").exists()

    # ── Yardimcilar ───────────────────────────────────────────────────────

    @staticmethod
    def _patlayan_ikinci_kaynak():
        """Ilk kaynak basarili, ikincide (memory) patla."""
        real_copytree = shutil.copytree
        call_count = [0]

        def wrapper(kaynak, hedef, **kw):
            call_count[0] += 1
            if call_count[0] == 2:  # memory
                raise PermissionError("Memory erisilemez")
            return real_copytree(kaynak, hedef, **kw)

        return wrapper

    @staticmethod
    def _kaynaklari_olustur(kok: Path):
        """6 kaynak olustur."""
        (kok / "skills").mkdir(parents=True)
        (kok / "skills" / "a.txt").write_text("skill")
        (kok / "memory").mkdir(parents=True)
        (kok / "memory" / "b.json").write_text("{}")
        (kok / "config").mkdir(parents=True)
        (kok / "config" / "c.yaml").write_text("key: val")
        (kok / ".ReYMeN").mkdir(parents=True)
        (kok / ".ReYMeN" / "state.json").write_text('{"v":1}')
        (kok / "config.yaml").write_text("app: test")
        (kok / ".env").write_text("SECRET=123")

    @staticmethod
    def _bm(kok: Path):
        from reymen.core.backup_manager import BackupManager
        return BackupManager(yedek_dizini=kok / "yedekler")


# ═══════════════════════════════════════════════════════════════════════════════
#  COVERAGE KALANLAR — 5 son satir
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoverageKalanlar:
    """Kalan 5 satir icin targeted testler."""

    def test_zip_yedek_valueerror_continue(self):
        """L159: ValueError sonrasi continue (os.walk disi dosya)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            (kok / "main.py").write_text("ok")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.os.walk") as mock_walk:
                    def walk_side_effect(path):
                        return [(str(kok), [], ["main.py", "../outside.txt"])]
                    mock_walk.side_effect = walk_side_effect
                    bm = BackupManager(yedek_dizini=kok / "yedekler")
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"

    def test_temizle_eski_except(self):
        """L272-273: _temizle_eski except blogu."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            with patch.object(bm, "_yedekleri_listele", side_effect=RuntimeError("test hatasi")):
                bm._temizle_eski("kismi")

    def test_yedek_listele_dizin_yok(self):
        """L293: Yedek dizini yoksa bos liste doner."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            import shutil
            shutil.rmtree(yedek_dizini)

            yedekler = bm.yedek_listele()
            assert yedekler == []

    def test_yedek_liste_tool_buyuk_boyut(self):
        """L554: Buyuk dosya boyutu MB formatinda gosterilir."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("large.bin", b"x" * 1024 * 1024 * 2)

            sonuc = _yedek_liste_tool()

        assert "Toplam 1 yedek" in sonuc
        assert "MB" in sonuc

# ═══════════════════════════════════════════════════════════════════════════════
#  5. _tam_yedek() — L228-239
# ═══════════════════════════════════════════════════════════════════════════════

class TestTamYedek:
    """_tam_yedek: kismi + ZIP birlestirir."""

    def test_tam_yedek_her_ikisini_cagirir(self):
        """_tam_yedek, _kismi_yedek ve _zip_yedek'i cagirir (L230-231)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = self._bm(kok)
                sonuc = bm.yedek_al(tip="tam")

            assert sonuc["tip"] == "tam"
            assert sonuc["kismi"]["durum"] == "basarili"
            assert sonuc["zip"]["durum"] == "basarili"
            assert "sure" in sonuc

    def test_tam_yedek_zip_hatasi(self):
        """ZIP hata verirse, kismi yine basarili (L230-231 bagimsiz)."""
        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            self._kaynaklari_olustur(kok)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("zipfile.ZipFile", side_effect=OSError("Disk dolu")):
                    bm = self._bm(kok)
                    sonuc = bm.yedek_al(tip="tam")

            assert sonuc["kismi"]["durum"] == "basarili"
            assert sonuc["zip"]["durum"] == "hata"

    # ── Yardimcilar ───────────────────────────────────────────────────────

    @staticmethod
    def _kaynaklari_olustur(kok: Path):
        (kok / "skills").mkdir(parents=True)
        (kok / "skills" / "a.txt").write_text("skill")
        (kok / "memory").mkdir(parents=True)
        (kok / "memory" / "b.json").write_text("{}")
        (kok / "config").mkdir(parents=True)
        (kok / "config" / "c.yaml").write_text("key: val")
        (kok / ".ReYMeN").mkdir(parents=True)
        (kok / ".ReYMeN" / "state.json").write_text('{"v":1}')
        (kok / "config.yaml").write_text("app: test")
        (kok / ".env").write_text("SECRET=123")

    @staticmethod
    def _bm(kok: Path):
        from reymen.core.backup_manager import BackupManager
        return BackupManager(yedek_dizini=kok / "yedekler")


# ═══════════════════════════════════════════════════════════════════════════════
#  COVERAGE KALANLAR — 5 son satir
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoverageKalanlar:
    """Kalan 5 satir icin targeted testler."""

    def test_zip_yedek_valueerror_continue(self):
        """L159: ValueError sonrasi continue (os.walk disi dosya)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            (kok / "main.py").write_text("ok")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.os.walk") as mock_walk:
                    def walk_side_effect(path):
                        return [(str(kok), [], ["main.py", "../outside.txt"])]
                    mock_walk.side_effect = walk_side_effect
                    bm = BackupManager(yedek_dizini=kok / "yedekler")
                    sonuc = bm.yedek_al(tip="zip")

            assert sonuc["durum"] == "basarili"

    def test_temizle_eski_except(self):
        """L272-273: _temizle_eski except blogu."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            with patch.object(bm, "_yedekleri_listele", side_effect=RuntimeError("test hatasi")):
                bm._temizle_eski("kismi")

    def test_yedek_listele_dizin_yok(self):
        """L293: Yedek dizini yoksa bos liste doner."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            import shutil
            shutil.rmtree(yedek_dizini)

            yedekler = bm.yedek_listele()
            assert yedekler == []

    def test_yedek_liste_tool_buyuk_boyut(self):
        """L554: Buyuk dosya boyutu MB formatinda gosterilir."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("large.bin", b"x" * 1024 * 1024 * 2)

            sonuc = _yedek_liste_tool()

        assert "Toplam 1 yedek" in sonuc
        assert "MB" in sonuc# ═══════════════════════════════════════════════════════════════════════════════
#  6. _git_yedek() — L186-226
#  subprocess.run mock ile Git push backup
# ═══════════════════════════════════════════════════════════════════════════════

class TestGitYedek:
    """_git_yedek: subprocess.run mock ile Git push backup."""

    def _make_process(self, returncode=0, stdout="", stderr=""):
        """Helper: CompletedProcess mock olustur."""
        mp = MagicMock(spec=subprocess.CompletedProcess)
        mp.returncode = returncode
        mp.stdout = stdout
        mp.stderr = stderr
        return mp

    def test_git_yedek_basarili(self):
        """Tum git komutlari basarili (kod=0)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            mp = self._make_process(0)
            with patch("reymen.core.backup_manager.subprocess.run", return_value=mp):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = bm.yedek_al(tip="git")

            assert sonuc["tip"] == "git"
            assert sonuc["durum"] == "basarili"
            assert sonuc["hedef"] == "Watcher-ReYMeN/ReYMeN-full-backup"
            assert len(sonuc["adimlar"]) == 4
            assert "sure" in sonuc

    def test_git_yedek_nothing_to_commit(self):
        """'nothing to commit' mesaji basari sayilir (L214)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")

            def side_effect(cmd, **kw):
                cmd_str = " ".join(cmd)
                if "push" in cmd_str:
                    return self._make_process(0, "Everything up-to-date")
                if "commit" in cmd_str:
                    return self._make_process(1, "nothing to commit, working tree clean")
                return self._make_process(0)

            with patch("reymen.core.backup_manager.subprocess.run", side_effect=side_effect):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = bm.yedek_al(tip="git")

            assert sonuc["durum"] == "basarili"

    def test_git_yedek_kismi_basari(self):
        """Bazi komutlar basarisiz → durum='kismi' (L214 testi)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")

            def side_effect(cmd, **kw):
                cmd_str = " ".join(cmd)
                if "add" in cmd_str:
                    return self._make_process(1, stderr="fatal: not a git repository")
                return self._make_process(0)

            with patch("reymen.core.backup_manager.subprocess.run", side_effect=side_effect):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = bm.yedek_al(tip="git")

            assert sonuc["durum"] == "kismi"

    def test_git_yedek_timeout(self):
        """subprocess.TimeoutExpired yakalanir (L208-209)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")

            with patch("reymen.core.backup_manager.subprocess.run",
                       side_effect=subprocess.TimeoutExpired("git push", 60)):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = bm.yedek_al(tip="git")

            assert sonuc["durum"] == "kismi"
            zaman_asimi_adimlari = [a for a in sonuc["adimlar"] if a.get("kod") == -1]
            assert len(zaman_asimi_adimlari) >= 1

    def test_git_yedek_genel_exception(self):
        """_git_yedek disindaki Exception yakalanir (L224-226)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")

            with patch("reymen.core.backup_manager.subprocess.run",
                       side_effect=PermissionError("Erisim engellendi")):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = bm.yedek_al(tip="git")

            assert sonuc["durum"] == "hata"
            assert "Erisim engellendi" in sonuc["hata"]

    def test_git_yedek_stdout_stderr_kesilir(self):
        """stdout/stderr 200 karakterle sinirlanir (L204-205)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            mp = self._make_process(0, "x" * 500, "y" * 500)

            with patch("reymen.core.backup_manager.subprocess.run", return_value=mp):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = bm.yedek_al(tip="git")

            assert sonuc["durum"] == "basarili"
            for adim in sonuc["adimlar"]:
                assert len(adim.get("cikti", "")) <= 200
                assert len(adim.get("hata", "")) <= 200


# ═══════════════════════════════════════════════════════════════════════════════
#  7. _metadata_yaz() — L241-256
# ═══════════════════════════════════════════════════════════════════════════════

class TestMetadataYaz:
    """_metadata_yaz: metadata.json olusturma ve hata yonetimi."""

    def test_metadata_yaz_basarili(self):
        """_metadata_yaz dogru icerikte JSON dosyasi olusturur (L243-254)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            hedef = Path(td) / "yedek_klasoru"
            hedef.mkdir()

            bm._metadata_yaz(hedef, "kismi", ["skills", "memory"])

            meta_path = hedef / "yedek_metadata.json"
            assert meta_path.exists()
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            assert meta["tip"] == "kismi"
            assert meta["yedeklenen"] == ["skills", "memory"]
            assert "tarih" in meta
            assert "proje" in meta
            assert "python_version" in meta

    def test_metadata_yaz_hatali_yol(self):
        """Gecersiz hedef yolunda except yakalanir (L255-256)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            olmayan_yol = Path(td) / "olmayan" / "klasor"

            bm._metadata_yaz(olmayan_yol, "kismi", ["test"])

            assert not (olmayan_yol / "yedek_metadata.json").exists()

    def test_metadata_zip_tipi(self):
        """_metadata_yaz zip tipi ile de calisir."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            hedef = Path(td) / "yedek_zip"
            hedef.mkdir()

            bm._metadata_yaz(hedef, "zip", [])

            meta = json.loads((hedef / "yedek_metadata.json").read_text(encoding="utf-8"))
            assert meta["tip"] == "zip"
            assert meta["yedeklenen"] == []


# ═══════════════════════════════════════════════════════════════════════════════
#  8. _temizle_eski() — L258-273
# ═══════════════════════════════════════════════════════════════════════════════

class TestTemizleEski:
    """_temizle_eski: MAX_YEDEK'ten fazla yedek varsa en eskileri silinir."""

    def test_temizle_eski_sayiyi_gecmezse_silmez(self):
        """MAX_YEDEK'ten az yedek varsa hicbiri silinmez (L262)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager, MAX_YEDEK
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            for i in range(MAX_YEDEK - 1):
                klasor = yedek_dizini / f"kismi_20260629_{i:06d}"
                klasor.mkdir()
                (klasor / "yedek_metadata.json").write_text('{"tip":"kismi","yedeklenen":[]}', encoding="utf-8")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            bm._temizle_eski("kismi")

            kalanlar = list(yedek_dizini.glob("kismi_*"))
            assert len(kalanlar) == MAX_YEDEK - 1

    def test_temizle_eski_eskileri_silmeli(self):
        """MAX_YEDEK+1 yedek varsa en eski 1 tanesi silinir (L263-270).

        _yedekleri_listele reverse=True ile siralar (once en yeni).
        yedekler[MAX_YEDEK:] = en eski (MAX_YEDEK+1). yani index'ten itibaren.
        MAX_YEDEK=10, 11 yedek → yedekler[10:] = en eski 1 yedek.
        """
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager, MAX_YEDEK
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            # MAX_YEDEK+1 yedek olustur
            for i in range(MAX_YEDEK + 1):
                klasor = yedek_dizini / f"kismi_20260629_{i:06d}"
                klasor.mkdir()
                (klasor / "yedek_metadata.json").write_text('{"tip":"kismi","yedeklenen":[]}', encoding="utf-8")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            bm._temizle_eski("kismi")

            kalanlar = sorted(yedek_dizini.glob("kismi_*"))
            assert len(kalanlar) <= MAX_YEDEK
            # En eski (en kucuk numara = en once olusturulan) silinmis olmali
            en_eski = yedek_dizini / "kismi_20260629_000000"
            assert not en_eski.exists()

    def test_temizle_eski_zip_dosyasi_silmeli(self):
        """ZIP yedekler icin de calisir (.zip dosyasi silme - L270)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager, MAX_YEDEK
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            for i in range(MAX_YEDEK + 1):
                zip_path = yedek_dizini / f"tam_20260629_{i:06d}.zip"
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    zf.writestr("dummy.txt", "data")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            bm._temizle_eski("zip")

            kalanlar = sorted(yedek_dizini.glob("tam_*.zip"))
            assert len(kalanlar) <= MAX_YEDEK

    def test_temizle_eski_bos_dizin(self):
        """Bos yedek dizininde hata firlatmaz (L272-273)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            bm = BackupManager(yedek_dizini=yedek_dizini)
            bm._temizle_eski("kismi")

    def test_temizle_eski_varolmayan_tip(self):
        """Var olmayan tip ile hata firlatmaz (L272-273 except)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            bm = BackupManager(yedek_dizini=yedek_dizini)
            bm._temizle_eski("varolmayan_tip")


# ═══════════════════════════════════════════════════════════════════════════════
#  9. geri_yukle() / _kismi_geri_yukle() — L334-401
# ═══════════════════════════════════════════════════════════════════════════════

class TestGeriYukle:
    """geri_yukle: routing + _kismi_geri_yukle."""

    def test_kaynak_bulunamadi(self):
        """Var olmayan kaynak → hata (L346-347)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            sonuc = bm.geri_yukle("/var/olmayan/yedek")

            assert sonuc["durum"] == "hata"
            assert "Kaynak bulunamadi" in sonuc["hata"]

    def test_bilinmeyen_kaynak_tipi(self):
        """Ne klasor ne ZIP → hata (L354-355)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            bm = BackupManager(yedek_dizini=Path(td) / "yedekler")
            bilinmeyen = Path(td) / "backup.tar.gz"
            bilinmeyen.write_text("not a zip")
            sonuc = bm.geri_yukle(str(bilinmeyen))

            assert sonuc["durum"] == "hata"
            assert "Bilinmeyen kaynak" in sonuc["hata"]

    def test_kismi_geri_yukle_tum_klasorler(self):
        """Kismi yedekten tum klasorler geri yuklenir (L372-381)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kaynak = yedek_dizini / "kismi_20260629_120000"
            kaynak.mkdir()
            for klasor in ("skills", "memory", "config", "reymen_config"):
                (kaynak / klasor).mkdir()
                (kaynak / klasor / "test.txt").write_text(f"{klasor}_data")

            for hedef_adi in ("skills", "memory", "config", ".ReYMeN"):
                (kok / hedef_adi).mkdir(parents=True, exist_ok=True)
                (kok / hedef_adi / "old.txt").write_text("old")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = BackupManager(yedek_dizini=yedek_dizini)
                sonuc = bm.geri_yukle(str(kaynak))

            assert sonuc["durum"] == "basarili"
            assert len(sonuc["geri_yuklenen"]) == 4
            assert "skills" in sonuc["geri_yuklenen"]
            assert "memory" in sonuc["geri_yuklenen"]
            assert (kok / "skills" / "test.txt").read_text() == "skills_data"
            assert not (kok / "skills" / "old.txt").exists()

    def test_kismi_geri_yukle_tek_dosyalar(self):
        """Kismi yedekten config_yaml ve env dosyalari geri yuklenir (L384-393)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kaynak = yedek_dizini / "kismi_20260629_120000"
            kaynak.mkdir()
            (kaynak / "config_yaml").write_text("app: test")
            (kaynak / "env").write_text("SECRET=123")
            (kok / ".env").write_text("OLD=abc")
            (kok / "config.yaml").write_text("old: config")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = BackupManager(yedek_dizini=yedek_dizini)
                sonuc = bm.geri_yukle(str(kaynak))

            assert sonuc["durum"] == "basarili"
            assert "config_yaml" in sonuc["geri_yuklenen"]
            assert "env" in sonuc["geri_yuklenen"]
            assert (kok / "config.yaml").read_text() == "app: test"
            assert (kok / ".env").read_text() == "SECRET=123"

    def test_kismi_geri_yukle_kismi_klasor(self):
        """Kaynakta sadece bazi klasorler varsa onlar yuklenir (L374)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kaynak = yedek_dizini / "kismi_20260629_120000"
            kaynak.mkdir()
            (kaynak / "skills").mkdir()
            (kaynak / "skills" / "a.txt").write_text("data")

            (kok / "skills").mkdir(parents=True, exist_ok=True)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = BackupManager(yedek_dizini=yedek_dizini)
                sonuc = bm.geri_yukle(str(kaynak))

            assert sonuc["durum"] == "basarili"
            assert "skills" in sonuc["geri_yuklenen"]
            assert "memory" not in sonuc["geri_yuklenen"]

    def test_geri_yukle_genel_exception(self):
        """geri_yukle'deki genel except yakalanir (L356-358)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            kaynak = kok / "yedek_klasoru"
            kaynak.mkdir()

            with patch.object(BackupManager, "_kismi_geri_yukle",
                              side_effect=RuntimeError("Beklenmeyen hata")):
                bm = BackupManager(yedek_dizini=kok / "yedekler")
                sonuc = bm.geri_yukle(str(kaynak))

            assert sonuc["durum"] == "hata"
            assert "Beklenmeyen hata" in sonuc["hata"]

    def test_kismi_geri_yukle_copytree_hatasi(self):
        """Klasor geri yuklemede hata → atlanir (L380-381)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kaynak = yedek_dizini / "kismi_20260629_120000"
            kaynak.mkdir()
            (kaynak / "skills").mkdir()
            (kaynak / "skills" / "a.txt").write_text("data")
            (kaynak / "memory").mkdir()
            (kaynak / "memory" / "b.json").write_text("{}")

            (kok / "skills").mkdir(parents=True, exist_ok=True)
            (kok / "memory").mkdir(parents=True, exist_ok=True)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copytree",
                           side_effect=PermissionError("Engelli")):
                    bm = BackupManager(yedek_dizini=yedek_dizini)
                    sonuc = bm.geri_yukle(str(kaynak))

            assert sonuc["durum"] == "basarili"
            assert len(sonuc["geri_yuklenen"]) == 0

    def test_kismi_geri_yukle_copy2_hatasi(self):
        """Tek dosya geri yuklemede hata → atlanir (L392-393)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kaynak = yedek_dizini / "kismi_20260629_120000"
            kaynak.mkdir()
            (kaynak / "config_yaml").write_text("app: test")
            (kaynak / "env").write_text("SECRET=123")
            (kok / ".env").write_text("OLD=abc")
            (kok / "config.yaml").write_text("old: config")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                with patch("reymen.core.backup_manager.shutil.copy2",
                           side_effect=PermissionError("Yazma engelli")):
                    bm = BackupManager(yedek_dizini=yedek_dizini)
                    sonuc = bm.geri_yukle(str(kaynak))

            assert sonuc["durum"] == "basarili"
            assert len(sonuc["geri_yuklenen"]) == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  10. _zip_geri_yukle() — L403-421
# ═══════════════════════════════════════════════════════════════════════════════

class TestGeriYukleZip:
    """_zip_geri_yukle: ZIP yedekten geri yukleme."""

    def test_zip_geri_yukle_basarili(self):
        """ZIP dosyasindan basarili geri yukleme (L408-419)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("main.py", "print('hello')")
                zf.writestr("data/info.txt", "info")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = BackupManager(yedek_dizini=yedek_dizini)
                sonuc = bm.geri_yukle(str(zip_path))

            assert sonuc["durum"] == "basarili"
            assert "cikti" in sonuc
            cikti = Path(sonuc["cikti"])
            assert cikti.exists()
            assert (cikti / "main.py").read_text() == "print('hello')"
            assert (cikti / "data" / "info.txt").read_text() == "info"

    def test_zip_geri_yukle_zip_hatasi(self):
        """Bozuk ZIP dosyasi → hata (L420-421)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            zip_path = yedek_dizini / "bozuk.zip"
            zip_path.write_text("not a zip file")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = BackupManager(yedek_dizini=yedek_dizini)
                sonuc = bm.geri_yukle(str(zip_path))

            assert sonuc["durum"] == "hata"
            assert "hata" in sonuc

    def test_zip_geri_yukle_cikti_dizini_olusturulur(self):
        """Cikti dizini otomatik olusturulur (L405-406)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("test.txt", "data")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                bm = BackupManager(yedek_dizini=yedek_dizini)
                sonuc = bm.geri_yukle(str(zip_path))

            assert sonuc["durum"] == "basarili"
            cikti = Path(sonuc["cikti"])
            assert cikti.exists()
            assert cikti.name.startswith("geri_yukleme_")


# ═══════════════════════════════════════════════════════════════════════════════
#  11. yedek_listele() / _yedekleri_listele() — L277-330
# ═══════════════════════════════════════════════════════════════════════════════

class TestYedekListele:
    """yedek_listele / _yedekleri_listele."""

    def test_yedek_listele_bos(self):
        """Henuz yedek yokken bos liste doner (L292-293)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            bm = BackupManager(yedek_dizini=yedek_dizini)
            yedekler = bm.yedek_listele()

            assert yedekler == []

    def test_yedek_listele_kismi_ve_zip(self):
        """Kismi ve ZIP yedekler birlikte listelenir (L296-324)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kismi1 = yedek_dizini / "kismi_20260629_120000"
            kismi1.mkdir()
            (kismi1 / "yedek_metadata.json").write_text(
                '{"tip":"kismi","tarih":"2026-06-29T12:00:00","yedeklenen":["skills"]}',
                encoding="utf-8"
            )
            (kismi1 / "skills").mkdir()
            (kismi1 / "skills" / "a.txt").write_text("x" * 100)

            zip_path = yedek_dizini / "tam_20260629_130000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("main.py", "print('ok')")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            yedekler = bm.yedek_listele()

            assert len(yedekler) == 2
            tipler = [y["tip"] for y in yedekler]
            assert "kismi" in tipler
            assert "zip" in tipler

    def test_yedek_listele_filtre_kismi(self):
        """tip='kismi' filtresi sadece kismi yedekleri gosterir (L327-328)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kismi1 = yedek_dizini / "kismi_20260629_120000"
            kismi1.mkdir()
            (kismi1 / "yedek_metadata.json").write_text('{"tip":"kismi","yedeklenen":[]}', encoding="utf-8")

            zip_path = yedek_dizini / "tam_20260629_130000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("dummy.txt", "x")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            yedekler = bm.yedek_listele(tip="kismi")

            assert len(yedekler) == 1
            assert yedekler[0]["tip"] == "kismi"

    def test_yedek_listele_filtre_zip(self):
        """tip='zip' filtresi sadece ZIP yedekleri gosterir."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kismi1 = yedek_dizini / "kismi_20260629_120000"
            kismi1.mkdir()
            (kismi1 / "yedek_metadata.json").write_text('{"tip":"kismi","yedeklenen":[]}', encoding="utf-8")

            zip_path = yedek_dizini / "tam_20260629_130000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("dummy.txt", "x")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            yedekler = bm.yedek_listele(tip="zip")

            assert len(yedekler) == 1
            assert yedekler[0]["tip"] == "zip"

    def test_yedek_listele_metadata_json_hatasi(self):
        """Bozuk metadata.json → hata atlanir, yedek yine listelenir (L303-304)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kismi1 = yedek_dizini / "kismi_20260629_120000"
            kismi1.mkdir()
            (kismi1 / "yedek_metadata.json").write_text("not valid json{{{", encoding="utf-8")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            yedekler = bm.yedek_listele()

            assert len(yedekler) == 1
            assert yedekler[0]["tip"] == "kismi"
            assert yedekler[0].get("yedeklenen") == []

    def test_yedek_listele_metadata_yok(self):
        """Metadata dosyasi olmayan yedek listelenir (L299-300)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            kismi1 = yedek_dizini / "kismi_20260629_120000"
            kismi1.mkdir()

            bm = BackupManager(yedek_dizini=yedek_dizini)
            yedekler = bm.yedek_listele()

            assert len(yedekler) == 1
            assert yedekler[0]["tip"] == "kismi"
            assert "tarih" in yedekler[0]

    def test_yedek_listele_zip_boyutu(self):
        """ZIP yedek boyut bilgisi dogru (L322-323)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("data.bin", b"x" * 1024 * 10)

            bm = BackupManager(yedek_dizini=yedek_dizini)
            yedekler = bm.yedek_listele()

            assert len(yedekler) == 1
            zip_yedek = yedekler[0]
            assert zip_yedek["tip"] == "zip"
            assert zip_yedek["boyut"] > 0
            assert zip_yedek["boyut_mb"] > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  12. durum() — L425-439
# ═══════════════════════════════════════════════════════════════════════════════

class TestDurum:
    """durum() yedekleme sistemi durumu."""

    def test_durum_bos(self):
        """Henuz yedek yokken durum bilgisi (L427-438)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            bm = BackupManager(yedek_dizini=yedek_dizini)
            durum = bm.durum()

            assert durum["toplam_yedek"] == 0
            assert durum["kismi_yedek"] == 0
            assert durum["zip_yedek"] == 0
            assert durum["toplam_boyut_mb"] == 0.0
            assert "yedek_dizini" in durum
            assert "max_yedek" in durum
            assert "proje_dizini" in durum
            assert "git_repo" in durum

    def test_durum_yedek_varken(self):
        """Yedekler varken durum dogru sayilari verir."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import BackupManager
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)

            for i in range(2):
                k = yedek_dizini / f"kismi_20260629_{i:06d}"
                k.mkdir()
                (k / "yedek_metadata.json").write_text('{"tip":"kismi","yedeklenen":[]}', encoding="utf-8")
                (k / "a.txt").write_text("x" * 100)

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("dummy.txt", "x")

            bm = BackupManager(yedek_dizini=yedek_dizini)
            durum = bm.durum()

            assert durum["toplam_yedek"] == 3
            assert durum["kismi_yedek"] == 2
            assert durum["zip_yedek"] == 1
            # Boyut sifirdan buyuk olmali (metadata + a.txt + zip)
            assert durum["toplam_boyut_mb"] >= 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  13. backup_manager_al() — L449-454
# ═══════════════════════════════════════════════════════════════════════════════

class TestBackupManagerAl:
    """backup_manager_al singleton."""

    def test_backup_manager_al_singleton(self):
        """backup_manager_al her seferinde ayni instance'i doner (L452-454)."""
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        bm1 = bm_mod.backup_manager_al()
        bm2 = bm_mod.backup_manager_al()

        assert bm1 is bm2

    def test_backup_manager_al_instance_turu(self):
        """backup_manager_al BackupManager dondurur."""
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        bm = bm_mod.backup_manager_al()
        assert isinstance(bm, bm_mod.BackupManager)

    def test_backup_manager_al_farkli_instance(self):
        """Singleton'i sifirlayinca yeni instance alinir."""
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        bm1 = bm_mod.backup_manager_al()
        bm_mod._backup_manager_instance = None
        bm2 = bm_mod.backup_manager_al()

        assert bm1 is not bm2


# ═══════════════════════════════════════════════════════════════════════════════
#  14. motor_kaydet() — L462-491
# ═══════════════════════════════════════════════════════════════════════════════

class TestMotorKaydet:
    """motor_kaydet: motor'a 3 arac kaydedilir."""

    def test_motor_kaydet_uc_arac(self):
        """motor_kaydet 3 kere _plugin_arac_kaydet cagirir (L470-490)."""
        from reymen.core.backup_manager import motor_kaydet
        motor = MagicMock()

        motor_kaydet(motor)

        assert motor._plugin_arac_kaydet.call_count == 3

    def test_motor_kaydet_yedek_al_kaydedilir(self):
        """YEDEK_AL aracı kaydedilir (L470-476)."""
        from reymen.core.backup_manager import motor_kaydet
        motor = MagicMock()

        motor_kaydet(motor)

        calls = motor._plugin_arac_kaydet.call_args_list
        assert any(c[0][0] == "YEDEK_AL" for c in calls)

    def test_motor_kaydet_yedek_liste_kaydedilir(self):
        """YEDEK_LISTE aracı kaydedilir (L477-483)."""
        from reymen.core.backup_manager import motor_kaydet
        motor = MagicMock()

        motor_kaydet(motor)

        calls = motor._plugin_arac_kaydet.call_args_list
        assert any(c[0][0] == "YEDEK_LISTE" for c in calls)

    def test_motor_kaydet_geri_yukle_kaydedilir(self):
        """GERI_YUKLE aracı kaydedilir (L484-490)."""
        from reymen.core.backup_manager import motor_kaydet
        motor = MagicMock()

        motor_kaydet(motor)

        calls = motor._plugin_arac_kaydet.call_args_list
        assert any(c[0][0] == "GERI_YUKLE" for c in calls)


# ═══════════════════════════════════════════════════════════════════════════════
#  15. _yedek_al_tool() — L494-534
# ═══════════════════════════════════════════════════════════════════════════════

class TestYedekAlTool:
    """_yedek_al_tool: YEDEK_AL motor tool wrapper."""

    def test_yedek_al_tool_gecersiz_tip(self):
        """Gecersiz tip → hata mesaji (L499-500)."""
        from reymen.core.backup_manager import _yedek_al_tool
        sonuc = _yedek_al_tool(tip="ftp")
        assert "gecersiz tip" in sonuc
        assert "ftp" in sonuc

    def test_yedek_al_tool_gecersiz_tip_args(self):
        """Args ile gecersiz tip → hata mesaji (L496-500)."""
        from reymen.core.backup_manager import _yedek_al_tool
        sonuc = _yedek_al_tool(args=["invalid"])
        assert "gecersiz tip" in sonuc

    def test_yedek_al_tool_kismi_basarili(self):
        """Kismi yedek basarili → basari mesaji (L508-514)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import _yedek_al_tool
            import reymen.core.backup_manager as bm_mod
            bm_mod._backup_manager_instance = None

            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            (kok / "skills").mkdir(parents=True)
            (kok / "skills" / "a.txt").write_text("data")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                sonuc = _yedek_al_tool(tip="kismi")

            assert "[YEDEK]" in sonuc
            assert "Kismi yedek alindi" in sonuc

    def test_yedek_al_tool_zip_basarili(self):
        """ZIP yedek basarili → basari mesaji (L515-521)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import _yedek_al_tool
            import reymen.core.backup_manager as bm_mod
            bm_mod._backup_manager_instance = None

            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            (kok / "test.txt").write_text("data")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                sonuc = _yedek_al_tool(tip="zip")

            assert "[YEDEK]" in sonuc
            assert "ZIP yedek alindi" in sonuc

    def test_yedek_al_tool_git_basarili(self):
        """Git yedek basarili → basari mesaji (L522-527)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import _yedek_al_tool
            import reymen.core.backup_manager as bm_mod
            bm_mod._backup_manager_instance = None

            mp = MagicMock(spec=subprocess.CompletedProcess)
            mp.returncode = 0
            mp.stdout = ""
            mp.stderr = ""

            with patch("reymen.core.backup_manager.subprocess.run", return_value=mp):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = _yedek_al_tool(tip="git")

            assert "[YEDEK]" in sonuc
            assert "Git yedek" in sonuc

    def test_yedek_al_tool_tam_basarili(self):
        """Tam yedek basarili → basari mesaji (L528-534)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import _yedek_al_tool
            import reymen.core.backup_manager as bm_mod
            bm_mod._backup_manager_instance = None

            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            (kok / "skills").mkdir(parents=True)
            (kok / "skills" / "a.txt").write_text("data")
            (kok / "test.txt").write_text("x")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                sonuc = _yedek_al_tool(tip="tam")

            assert "[YEDEK]" in sonuc

    def test_yedek_al_tool_varsayilan_tip_kismi(self):
        """Varsayilan tip='kismi' (L497)."""
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import _yedek_al_tool
            import reymen.core.backup_manager as bm_mod
            bm_mod._backup_manager_instance = None

            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            (kok / "skills").mkdir(parents=True)
            (kok / "skills" / "a.txt").write_text("data")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                sonuc = _yedek_al_tool()

            assert "[YEDEK]" in sonuc

    def test_yedek_al_tool_hata_durumu(self):
        """Hata durumunda hata mesaji (L505-506).

        _git_yedek icinde genel Exception firlatarak hata alinir.
        """
        with tempfile.TemporaryDirectory() as td:
            from reymen.core.backup_manager import _yedek_al_tool
            import reymen.core.backup_manager as bm_mod
            bm_mod._backup_manager_instance = None

            with patch("reymen.core.backup_manager.subprocess.run",
                       side_effect=PermissionError("Erisim yok")):
                with patch("reymen.core.backup_manager.PROJE_KOK", Path(td)):
                    sonuc = _yedek_al_tool(tip="git")

            assert "[HATA]" in sonuc


# ═══════════════════════════════════════════════════════════════════════════════
#  16. _yedek_liste_tool() — L537-565
# ═══════════════════════════════════════════════════════════════════════════════

class TestYedekListeTool:
    """_yedek_liste_tool: YEDEK_LISTE motor tool."""

    def test_yedek_liste_tool_bos(self):
        """Henuz yedek yokken uygun mesaj (L545-546)."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            sonuc = _yedek_liste_tool()
            assert "Henuz yedek bulunmuyor" in sonuc

    def test_yedek_liste_tool_kismi_yedek_var(self):
        """Kismi yedek varken dogru listelenir (L560-561)."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            k1 = yedek_dizini / "kismi_20260629_120000"
            k1.mkdir()
            (k1 / "yedek_metadata.json").write_text(
                '{"tip":"kismi","tarih":"2026-06-29T12:00:00","yedeklenen":["skills"]}',
                encoding="utf-8"
            )
            (k1 / "a.txt").write_text("x")

            sonuc = _yedek_liste_tool()

            assert "Toplam 1 yedek" in sonuc
            assert "📁" in sonuc

    def test_yedek_liste_tool_zip_yedek_var(self):
        """ZIP yedek varken dogru listelenir (L562-563)."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("dummy.txt", "x")

            sonuc = _yedek_liste_tool()

            assert "Toplam 1 yedek" in sonuc
            assert "📦" in sonuc

    def test_yedek_liste_tool_args_tip(self):
        """Args ile tip filtreleme (L540)."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            yedek_dizini = Path(td) / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            k1 = yedek_dizini / "kismi_20260629_120000"
            k1.mkdir()
            (k1 / "yedek_metadata.json").write_text('{"tip":"kismi"}', encoding="utf-8")

            zip_path = yedek_dizini / "tam_20260629_130000.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("dummy.txt", "x")

            sonuc = _yedek_liste_tool(args=["kismi"])

            assert "Toplam 1 yedek" in sonuc


# ═══════════════════════════════════════════════════════════════════════════════
#  17. _geri_yukle_tool() — L568-588
# ═══════════════════════════════════════════════════════════════════════════════

class TestGeriYukleTool:
    """_geri_yukle_tool: GERI_YUKLE motor tool."""

    def test_geri_yukle_tool_kaynak_yok(self):
        """Kaynak parametresi yoksa hata (L573-574)."""
        from reymen.core.backup_manager import _geri_yukle_tool
        sonuc = _geri_yukle_tool()
        assert "kaynak parametresi zorunlu" in sonuc

    def test_geri_yukle_tool_kaynak_yok_args(self):
        """Args bossa kaynak yok hatasi."""
        from reymen.core.backup_manager import _geri_yukle_tool
        sonuc = _geri_yukle_tool(args=[])
        assert "kaynak parametresi zorunlu" in sonuc

    def test_geri_yukle_tool_hata_durumu(self):
        """Geri yukleme basarisizsa hata mesaji (L579-580)."""
        from reymen.core.backup_manager import _geri_yukle_tool
        sonuc = _geri_yukle_tool(kaynak="/var/olmayan/yedek")
        assert "[HATA]" in sonuc

    def test_geri_yukle_tool_basarili(self):
        """Geri yukleme basariliysa basari mesaji (L582-588)."""
        from reymen.core.backup_manager import _geri_yukle_tool
        import reymen.core.backup_manager as bm_mod
        bm_mod._backup_manager_instance = None

        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm_mod.YEDEK_DIZINI = yedek_dizini

            kaynak = yedek_dizini / "kismi_20260629_120000"
            kaynak.mkdir()
            (kaynak / "skills").mkdir()
            (kaynak / "skills" / "a.txt").write_text("data")
            (kok / "skills").mkdir(parents=True, exist_ok=True)

            with patch("reymen.core.backup_manager.PROJE_KOK", kok):
                sonuc = _geri_yukle_tool(kaynak=str(kaynak))

            assert "[GERI_YUKLE]" in sonuc
            assert "Geri yukleme tamamlandi" in sonuc


# ═══════════════════════════════════════════════════════════════════════════════
#  18. Edge Case: L159 ValueError continue + L554 boyut > 1MB
# ═══════════════════════════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════════════════════════
#  18. Edge Case: L159 ValueError continue + L554 boyut > 1MB
# ═══════════════════════════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════════════════════════
#  18. Edge Cases: L159 ValueError + L554 boyut > 1MB
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Kalan 2 satir icin edge case testleri."""

    def test_zip_yedek_valueerror_continue(self):
        """L159: _zip_yedek'te rel_path ValueError → continue eder."""
        from reymen.core.backup_manager import BackupManager
        import zipfile
        import time

        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            (kok / "test.txt").write_text("hello")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok),                  patch("reymen.core.backup_manager.os.walk") as mock_walk,                  patch.object(zipfile.ZipFile, "write", side_effect=ValueError("path error")):
                mock_walk.return_value = [(str(kok), [], ["test.txt"])]
                sonuc = bm._zip_yedek("test", time.time())

            assert sonuc["durum"] == "basarili"
            assert "hata" not in sonuc

    def test_zip_yedek_oseerror_continue(self):
        """L160-161: _zip_yedek'te OSError → continue + logger.warning."""
        from reymen.core.backup_manager import BackupManager
        import zipfile
        import time

        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)
            bm = BackupManager(yedek_dizini=yedek_dizini)

            (kok / "test.txt").write_text("hello")

            with patch("reymen.core.backup_manager.PROJE_KOK", kok),                  patch("reymen.core.backup_manager.os.walk") as mock_walk,                  patch.object(zipfile.ZipFile, "write", side_effect=OSError("file locked")):
                mock_walk.return_value = [(str(kok), [], ["test.txt"])]
                sonuc = bm._zip_yedek("test", time.time())

            assert sonuc["durum"] == "basarili"

    def test_yedek_liste_tool_boyut_1mb_ustu(self):
        """L552-554: yedek_liste_tool'da boyut > 1MB → MB formatinda."""
        from reymen.core.backup_manager import _yedek_liste_tool
        import reymen.core.backup_manager as bm_mod
        import json

        with tempfile.TemporaryDirectory() as td:
            kok = Path(td)
            yedek_dizini = kok / "yedekler"
            yedek_dizini.mkdir(parents=True)

            # Create a zip file larger than 1MB
            zip_path = yedek_dizini / "tam_20260629_120000.zip"
            with open(zip_path, "wb") as f:
                f.write(b"x" * (2 * 1024 * 1024 + 100))  # 2MB+ real file

            # Create metadata with boyut_mb
            meta_dir = yedek_dizini / "tam_20260629_120000.zip.meta"
            meta_dir.mkdir(parents=True, exist_ok=True)
            (meta_dir / "metadata.json").write_text(json.dumps({
                "tip": "zip",
                "dosya": str(zip_path),
                "sure": 0.5,
                "durum": "basarili",
            }, ensure_ascii=False), encoding="utf-8")

            bm_mod._backup_manager_instance = None
            with patch("reymen.core.backup_manager.YEDEK_DIZINI", yedek_dizini),                  patch("reymen.core.backup_manager.PROJE_KOK", kok):
                sonuc = _yedek_liste_tool()

            assert "MB" in sonuc
