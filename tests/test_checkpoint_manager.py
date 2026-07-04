# -*- coding: utf-8 -*-
"""tests/test_checkpoint_manager.py — CheckpointManager kapsamlı test."""

import json
import sys
import os
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import reymen.sistem.checkpoint_manager as cm
from reymen.sistem.checkpoint_manager import CheckpointManager


class TestCheckpointManagerInit:
    """Başlangıç durumu."""

    def test_son_kayit_bos(self):
        cp = CheckpointManager()
        assert cp._son_kayit is None


class TestKaydet:
    """kaydet() — checkpoint oluşturma."""

    def test_donus_tipi_id(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("gorev1", 1, {"adimlar": []})
            assert cid.startswith("ckpt_")

    def test_dosya_olustu(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("gorev1", 1, {"x": 1})
            assert (tmp_path / f"{cid}.json").exists()

    def test_dosya_icerigi(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("gorev1", 3, {"adimlar": ["a", "b"]})
            veri = json.loads((tmp_path / f"{cid}.json").read_text(encoding="utf-8"))
            assert veri["id"] == cid
            assert veri["hedef"] == "gorev1"
            assert veri["tur"] == 3
            assert veri["durum"]["adimlar"] == ["a", "b"]
            assert "zaman" in veri

    def test_son_kayit_guncellendi(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("test", 1, {})
            assert cp._son_kayit == cid

    def test_unicode_icerik(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("Türkçe görev", 1, {"mesaj": "şçğıöü"})
            veri = json.loads((tmp_path / f"{cid}.json").read_text(encoding="utf-8"))
            assert veri["hedef"] == "Türkçe görev"
            assert veri["durum"]["mesaj"] == "şçğıöü"


class TestYukle:
    """yukle() — checkpoint okuma."""

    def test_mevcut_checkpoint(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("gorev1", 2, {"x": 42})
            yuklenen = cp.yukle(cid)
            assert yuklenen is not None
            assert yuklenen["tur"] == 2
            assert yuklenen["durum"]["x"] == 42

    def test_olmayan_checkpoint(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            assert cp.yukle("ckpt_9999999999") is None

    def test_bozuk_json(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            (tmp_path / "ckpt_bozuk.json").write_text("NOT JSON", encoding="utf-8")
            cp = CheckpointManager()
            assert cp.yukle("ckpt_bozuk") is None


class TestSonCheckpoint:
    """son_checkpoint() — en son checkpoint."""

    def test_son_kayit_varsa_o_donusur(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cp.kaydet("eskileri", 1, {})
            cid2 = cp.kaydet("yeni", 5, {"a": 1})
            son = cp.son_chekpoint()
            assert son["id"] == cid2
            assert son["tur"] == 5

    def test_kayit_yoksa_dosyalardan_son(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            # Manuel dosya oluştur (kaydetmeden)
            veri = {
                "id": "ckpt_001",
                "hedef": "test",
                "tur": 1,
                "zaman": time.time(),
                "durum": {},
            }
            (tmp_path / "ckpt_001.json").write_text(json.dumps(veri), encoding="utf-8")
            cp = CheckpointManager()
            son = cp.son_chekpoint()
            assert son is not None
            assert son["id"] == "ckpt_001"

    def test_hic_checkpoint_yok(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            assert cp.son_chekpoint() is None

    def test_boyut_fazla_buyuk_dosya(self, tmp_path):
        """Son dosya okunamıyorsa None döner."""
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            (tmp_path / "ckpt_999.json").write_text("!!!", encoding="utf-8")
            cp = CheckpointManager()
            assert cp.son_chekpoint() is None


class TestListele:
    """listele() — tüm checkpoint'leri listele."""

    def test_bos_liste(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            assert cp.listele() == []

    def test_coklu_liste(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path), patch(
            "reymen.sistem.checkpoint_manager.time"
        ) as mock_time:
            mock_time.time.return_value = 1000.0
            mock_time.strftime.side_effect = lambda fmt, t: "00:00:00"
            mock_time.localtime.side_effect = lambda t: (2025, 1, 1, 0, 0, 0, 0, 0, 0)
            cp = CheckpointManager()
            cp.kaydet("gorev_A", 1, {})
            mock_time.time.return_value = 1001.0
            cp.kaydet("gorev_B", 2, {})
            liste = cp.listele()
            assert len(liste) == 2
            assert liste[0]["hedef"] == "gorev_A"
            assert liste[1]["hedef"] == "gorev_B"

    def test_liste_keys(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cp.kaydet("test", 1, {})
            liste = cp.listele()
            keys = set(liste[0].keys())
            assert keys == {"id", "hedef", "tur", "zaman"}

    def test_hedef_kisitlama_50(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            uzun = "A" * 100
            cp.kaydet(uzun, 1, {})
            liste = cp.listele()
            assert len(liste[0]["hedef"]) <= 50

    def test_bozuk_dosya_atlanir(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            (tmp_path / "ckpt_bos.json").write_text("{}", encoding="utf-8")
            cp = CheckpointManager()
            liste = cp.listele()  # hata fırlatmamalı
            assert isinstance(liste, list)


class TestTemizle:
    """temizle() — eski checkpoint temizleme."""

    def test_yeni_dosya_silinmez(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cp.kaydet("yeni", 1, {})
            cp.temizle(saatten_eski=24)
            assert len(list(tmp_path.glob("ckpt_*.json"))) == 1

    def test_eski_dosya_silinir(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("eski", 1, {})
            # Dosya zamanını 25 saat geriye al
            dosya = tmp_path / f"{cid}.json"
            eski_zaman = time.time() - (25 * 3600)
            os.utime(dosya, (eski_zaman, eski_zaman))
            cp.temizle(saatten_eski=24)
            assert not dosya.exists()

    def test_sinirdaki_dosya_silinmez(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cid = cp.kaydet("sinir", 1, {})
            dosya = tmp_path / f"{cid}.json"
            # Tam 24 saat önce → silinmemeli (mtime >= sinir)
            sinir_zaman = time.time() - (24 * 3600) + 1
            os.utime(dosya, (sinir_zaman, sinir_zaman))
            cp.temizle(saatten_eski=24)
            assert dosya.exists()


class TestDevamEdilebilirMi:
    """devam_edebilir_mi() — hedefe göre checkpoint arama."""

    def test_mevcut_hedef(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cp.kaydet("gorev_xyz", 3, {"devam": True})
            sonuc = cp.devam_edebilir_mi("gorev_xyz")
            assert sonuc is not None
            assert sonuc["tur"] == 3

    def test_olmayan_hedef(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cp.kaydet("baska_gorev", 1, {})
            sonuc = cp.devam_edebilir_mi("yok böle_gorev")
            assert sonuc is None

    def test_tur_sifir_olmaz(self, tmp_path):
        """tur=0 olan checkpoint devam_edilebilir_mi'de görünmez."""
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            cp = CheckpointManager()
            cp.kaydet("gorev", 0, {})
            sonuc = cp.devam_edebilir_mi("gorev")
            assert sonuc is None


class TestAnaModul:
    """__main__ bloğu."""

    def test_modul_calisiyor(self, tmp_path):
        with patch.object(cm, "CHECKPOINT_DIR", tmp_path):
            # __main__ bloğu sadece print eder
            cp = CheckpointManager()
            cp.kaydet("test", 1, {"adimlar": ["yapildi"]})
            son = cp.son_chekpoint()
            assert son["hedef"] == "test"
