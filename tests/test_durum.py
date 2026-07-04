"""Test: reymen.sistem.durum — merkezi durum.json okuyucu."""

import sys, os, json, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Proje kokunu path'e ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.reymen.sistem.durum import durum_oku, motor_kaydet

# Module path for patching (must match the import source)
_MOD = "src.reymen.sistem.durum"


class TestDurumOku:
    """durum_oku — ana API fonksiyonu."""

    def test_varsayilan_ozet_dondurur(self, tmp_path):
        """Varsayilan parametre ile ozet dondurur."""
        dosya = tmp_path / "durum.json"
        veri = {"son_guncelleme": "2025-01-15", "tamam": 5, "toplam_ozellik": 10}
        dosya.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
        with patch(f"{_MOD}.DURUM_DOSYASI", dosya):
            sonuc = durum_oku()
            assert isinstance(sonuc, str)
            assert "ReYMeN Durum Raporu" in sonuc

    def test_detayli_mod(self, tmp_path):
        """detay=1 ile JSON formatinda detay dondurur."""
        dosya = tmp_path / "durum.json"
        dosya.write_text(json.dumps({"proje": "test"}), encoding="utf-8")
        with patch(f"{_MOD}.DURUM_DOSYASI", dosya):
            sonuc = durum_oku(detay="1")
            assert '"proje"' in sonuc

    def test_json_mod_raw(self, tmp_path):
        """detay='json' ile ham JSON dondurulur."""
        dosya = tmp_path / "durum.json"
        dosya.write_text(json.dumps({"proje": "test"}), encoding="utf-8")
        with patch(f"{_MOD}.DURUM_DOSYASI", dosya):
            sonuc = durum_oku(detay="json")
            assert '"proje"' in sonuc

    def test_detay_synonyms(self, tmp_path):
        """detay='detayli' ve 'raw' da calisir."""
        dosya = tmp_path / "durum.json"
        dosya.write_text(json.dumps({"x": 1}), encoding="utf-8")
        with patch(f"{_MOD}.DURUM_DOSYASI", dosya):
            assert '"x"' in durum_oku(detay="detayli")
            assert '"x"' in durum_oku(detay="raw")

    def test_dosya_yoksa_hata_dict_dondurur(self):
        """Dosya yoksa {'hata': ...} dondurur."""
        with patch(f"{_MOD}.DURUM_DOSYASI", Path("/nonexistent/durum.json")):
            sonuc = durum_oku(detay="json")
            assert "hata" in sonuc
            assert "bulunamadi" in sonuc

    def test_bozuk_json_hata_dondurur(self, tmp_path):
        """Bozuk JSON dosyasi {'hata': ...} dondurur."""
        dosya = tmp_path / "durum.json"
        dosya.write_text("{bozuk json", encoding="utf-8")
        with patch(f"{_MOD}.DURUM_DOSYASI", dosya):
            sonuc = durum_oku(detay="json")
            # sonuc is a JSON string containing {"hata": "..."}
            veri = json.loads(sonuc)
            assert "hata" in veri
            assert "bozuk" in veri["hata"].lower() or "JSON" in veri["hata"]


class TestMotorKaydet:
    """motor_kaydet — motor'a DURUM_OKU tool'unu kaydeder."""

    def test_motor_kaydet_cagirir(self):
        """motor._plugin_arac_kaydet DURUM_OKU ve DURUM_DEGISIKLIK kaydeder."""
        motor = MagicMock()
        motor._plugin_arac_kaydet = MagicMock()
        motor_kaydet(motor)
        # motor_kaydet iki tool kaydeder: DURUM_OKU ve DURUM_DEGISIKLIK
        assert motor._plugin_arac_kaydet.call_count == 2
        args_0 = motor._plugin_arac_kaydet.call_args_list[0][0]
        assert args_0[0] == "DURUM_OKU"
        args_1 = motor._plugin_arac_kaydet.call_args_list[1][0]
        assert args_1[0] == "DURUM_DEGISIKLIK"

    def test_motor_kaydet_uyumsuz_motor(self):
        """_plugin_arac_kaydet olmayan motor'da hata vermez."""
        motor = object()
        motor_kaydet(motor)  # should not raise
