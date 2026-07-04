"""Test: reymen.sistem.durum — merkezi durum.json okuyucu."""

import sys, os, json, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Proje kokunu path'e ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.reymen.sistem.durum import _yukle, _ozet, _detayli, durum_oku, motor_kaydet


class TestYukle:
    """_yukle — durum.json dosyasini okuma."""

    def test_dosya_yoksa_hata_dict_dondurur(self):
        """Dosya yoksa {'hata': ...} dondurur."""
        with patch(
            "reymen.sistem.durum.DURUM_DOSYASI", Path("/nonexistent/durum.json")
        ):
            sonuc = _yukle()
            assert "hata" in sonuc
            assert "bulunamadi" in sonuc["hata"]

    def test_gecerli_json_okur(self, tmp_path):
        """Gecerli bir JSON dosyasini okur."""
        dosya = tmp_path / "durum.json"
        veri = {"proje": "ReYMeN", "tamam": 5}
        dosya.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
        with patch("reymen.sistem.durum.DURUM_DOSYASI", dosya):
            sonuc = _yukle()
            assert sonuc["proje"] == "ReYMeN"
            assert sonuc["tamam"] == 5

    def test_bozuk_json_hata_dondurur(self, tmp_path):
        """Bozuk JSON dosyasi {'hata': ...} dondurur."""
        dosya = tmp_path / "durum.json"
        dosya.write_text("{bozuk json", encoding="utf-8")
        with patch("reymen.sistem.durum.DURUM_DOSYASI", dosya):
            sonuc = _yukle()
            assert "hata" in sonuc
            assert "JSON" in sonuc["hata"]


class TestOzet:
    """_ozet — insan okunabilir ozet raporu."""

    ORNEK_VERI = {
        "son_guncelleme": "2025-01-15",
        "guncelleyen_bot": "test_bot",
        "toplam_ozellik": 10,
        "tamam": 5,
        "isleniyor": 3,
        "cozulen_8_onceki": {
            "tamam": 4,
            "toplam": 8,
            "maddeler": {"test_madde": {"detay": "test detay"}},
        },
        "cozulen_10_ikinci_dalga": {
            "tamam": 6,
            "toplam": 10,
            "maddeler": {"test_madde2": {"detay": "detay2", "oncelik": "YUKSEK"}},
        },
        "cozulen_4_kismen": {
            "tamam": 2,
            "toplam": 4,
            "maddeler": {"kismen_madde": {"detay": "kismen", "oncelik": "ORTA"}},
        },
        "mevcut_eksikler": {
            "tamam": 3,
            "toplam": 15,
            "maddeler": {
                "eksik1": {"durum": "tamam", "oncelik": "YUKSEK"},
                "eksik2": {"durum": "kismen", "oncelik": "ORTA"},
                "eksik3": {"durum": "stub", "oncelik": "DUSUK"},
                "eksik4": {"durum": "eksik", "oncelik": "ACIL", "cozuluyor": True},
            },
        },
        "pasa_38_karsilastirmasi": {
            "aciklama": "karsilastirma test",
            "maddeler": [
                {"eksik": "test1", "cozuldu_mu": "evet", "ReYMeN": "var"},
                {"eksik": "test2", "cozuldu_mu": "hayir", "ReYMeN": "yok"},
            ],
        },
    }

    def test_ozet_metin_dondurur(self):
        """_ozet() string dondurur."""
        sonuc = _ozet(self.ORNEK_VERI)
        assert isinstance(sonuc, str)
        assert "ReYMeN Durum Raporu" in sonuc
        assert "test_bot" in sonuc

    def test_ozet_bos_veri_calisir(self):
        """Bos veri ile de calisir."""
        sonuc = _ozet({})
        assert isinstance(sonuc, str)

    def test_ozet_uyari_ekler(self):
        """_meta.bot_yanlis_liste_var varsa uyari satiri eklenir."""
        veri = dict(self.ORNEK_VERI)
        veri["_meta"] = {"bot_yanlis_liste_var": True}
        sonuc = _ozet(veri)
        assert "uyari" in sonuc.lower() or "⚠" in sonuc

    def test_ozet_diger_maddeleri_ekler(self):
        """cozulen_diger varsa listelenir."""
        veri = dict(self.ORNEK_VERI)
        veri["cozulen_diger"] = {"maddeler": ["diger1", "diger2"]}
        sonuc = _ozet(veri)
        assert "Diger" in sonuc

    def test_ozet_eksik_durum_emoji(self):
        """Her durum turu icin dogru emoji kullanilir."""
        sonuc = _ozet(self.ORNEK_VERI)
        assert "✅" in sonuc
        assert "🔶" in sonuc
        assert "❌" in sonuc


class TestDetayli:
    """_detayli — JSON formatinda detay."""

    def test_json_metin_dondurur(self):
        sonuc = _detayli({"test": "deger"})
        assert isinstance(sonuc, str)
        assert '"test"' in sonuc


class TestDurumOku:
    """durum_oku — ana API fonksiyonu."""

    def test_varsayilan_ozet_dondurur(self, tmp_path):
        """Varsayilan parametre ile _ozet cagrilir."""
        dosya = tmp_path / "durum.json"
        dosya.write_text(json.dumps({"proje": "test"}), encoding="utf-8")
        with patch("reymen.sistem.durum.DURUM_DOSYASI", dosya):
            sonuc = durum_oku()
            assert isinstance(sonuc, str)
            assert "ReYMeN Durum Raporu" in sonuc or "hata" in sonuc

    def test_detayli_mod(self, tmp_path):
        """detay=1 ile _detayli cagrilir."""
        dosya = tmp_path / "durum.json"
        dosya.write_text(json.dumps({"proje": "test"}), encoding="utf-8")
        with patch("reymen.sistem.durum.DURUM_DOSYASI", dosya):
            sonuc = durum_oku(detay="1")
            assert '"proje"' in sonuc

    def test_json_mod_raw(self, tmp_path):
        """detay='json' ile ham JSON dondurulur."""
        dosya = tmp_path / "durum.json"
        dosya.write_text(json.dumps({"proje": "test"}), encoding="utf-8")
        with patch("reymen.sistem.durum.DURUM_DOSYASI", dosya):
            sonuc = durum_oku(detay="json")
            assert '"proje"' in sonuc

    def test_detay_synonyms(self, tmp_path):
        """detay='detayli' ve 'raw' da calisir."""
        dosya = tmp_path / "durum.json"
        dosya.write_text(json.dumps({"x": 1}), encoding="utf-8")
        with patch("reymen.sistem.durum.DURUM_DOSYASI", dosya):
            assert '"x"' in durum_oku(detay="detayli")
            assert '"x"' in durum_oku(detay="raw")


class TestMotorKaydet:
    """motor_kaydet — motor'a DURUM_OKU tool'unu kaydeder."""

    def test_motor_kaydet_cagirir(self):
        """motor._plugin_arac_kaydet cagrilir."""
        motor = MagicMock()
        motor._plugin_arac_kaydet = MagicMock()
        motor_kaydet(motor)
        motor._plugin_arac_kaydet.assert_called_once()
        args = motor._plugin_arac_kaydet.call_args[0]
        assert args[0] == "DURUM_OKU"

    def test_motor_kaydet_uyumsuz_motor(self):
        """_plugin_arac_kaydet olmayan motor'da hata vermez."""
        motor = object()
        motor_kaydet(motor)  # should not raise
