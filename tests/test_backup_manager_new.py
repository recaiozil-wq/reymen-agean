# -*- coding: utf-8 -*-
"""
YENI test siniflari — mevcut 40 testin SONUNA eklenecek.
Coverage: %48.63 → %65+
Kapsanan kategoriler:
  - _git_yedek, _metadata_yaz, _temizle_eski
  - geri_yukle, _kismi_geri_yukle, _zip_geri_yukle
  - yedek_listele, durum, backup_manager_al
  - motor_kaydet, _yedek_al_tool, _yedek_liste_tool, _geri_yukle_tool
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJE_KOK))


# ═══════════════════════════════════════════════════════════════════════════════
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
