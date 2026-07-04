"""Test: reymen/sistem/marketplace.py"""

from __future__ import annotations
import os, sys, json, tempfile
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


@pytest.fixture(autouse=True)
def _clean_katalog(monkeypatch, tmp_path):
    """Her test öncesi katalog dosyasını geçici bir yere yönlendir."""
    import reymen.sistem.marketplace as m

    # Geçici bir katalog JSON oluştur
    kat_path = tmp_path / "plugin_katalog.json"
    katalog_verileri = [
        {
            "ad": "test_plugin",
            "versiyon": "1.0.0",
            "aciklama": "Test plugin aciklamasi",
            "yazar": "test_yazar",
            "kaynak": "https://example.com/test_plugin.zip",
            "lisans": "MIT",
            "etiketler": ["test", "demo"],
            "bagimliliklar": [],
            "dokuman": "",
        },
        {
            "ad": "web_scraper",
            "versiyon": "2.1.0",
            "aciklama": "Web kazima araci",
            "yazar": "reymen",
            "kaynak": "https://example.com/web_scraper.zip",
            "lisans": "MIT",
            "etiketler": ["web", "scraping"],
            "bagimliliklar": ["requests"],
            "dokuman": "https://example.com/docs",
        },
    ]
    kat_path.write_text(
        json.dumps(katalog_verileri, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    monkeypatch.setattr(m, "KATALOG_DOSYASI", kat_path)

    # Plugin dizinini de geçici yap
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir(exist_ok=True)
    monkeypatch.setattr(m, "PLUGIN_DIZINI", plugin_dir)
    yield


class TestKatalogYukle:
    def test_katalog_yukle_basarili(self):
        from reymen.sistem.marketplace import _katalog_yukle

        veri = _katalog_yukle()
        assert len(veri) == 2
        assert veri[0]["ad"] == "test_plugin"

    def test_katalog_yukle_hatali_json(self, monkeypatch):
        import reymen.sistem.marketplace as m

        # Bozuk JSON yaz
        m.KATALOG_DOSYASI.write_text("Bozuk json{{{", encoding="utf-8")
        veri = m._katalog_yukle()
        # Uzaktan da bulamayinca bos liste doner
        assert veri == []


class TestListe:
    def test_liste(self):
        from reymen.sistem.marketplace import liste

        sonuc = liste()
        assert "ReYMeN Plugin Katalogu" in sonuc
        assert "test_plugin" in sonuc
        assert "web_scraper" in sonuc
        assert "Toplam: 2" in sonuc

    def test_liste_bos(self, monkeypatch):
        import reymen.sistem.marketplace as m

        m.KATALOG_DOSYASI.write_text("[]", encoding="utf-8")
        sonuc = m.liste()
        assert "Katalog bos" in sonuc


class TestAra:
    def test_ara_bulunan(self):
        from reymen.sistem.marketplace import ara

        sonuc = ara("test_plugin")
        assert "test_plugin" in sonuc

    def test_ara_kismi_eslesme(self):
        from reymen.sistem.marketplace import ara

        sonuc = ara("test")
        assert "test_plugin" in sonuc
        assert "1 sonuc" in sonuc

    def test_ara_aciklama(self):
        from reymen.sistem.marketplace import ara

        sonuc = ara("kazima")
        assert "web_scraper" in sonuc

    def test_ara_etiket(self):
        from reymen.sistem.marketplace import ara

        sonuc = ara("scraping")
        assert "web_scraper" in sonuc

    def test_ara_bulunamadi(self):
        from reymen.sistem.marketplace import ara

        sonuc = ara("nonexistent_plugin")
        assert "sonuc bulunamadi" in sonuc

    def test_ara_bos_katalog(self, monkeypatch):
        import reymen.sistem.marketplace as m

        m.KATALOG_DOSYASI.write_text("[]", encoding="utf-8")
        sonuc = m.ara("test")
        assert "Katalog bos" in sonuc


class TestBilgi:
    def test_bilgi_bulunan(self):
        from reymen.sistem.marketplace import bilgi

        sonuc = bilgi("test_plugin")
        assert "test_plugin" in sonuc
        assert "v1.0.0" in sonuc
        assert "test_yazar" in sonuc

    def test_bilgi_bulunamadi(self):
        from reymen.sistem.marketplace import bilgi

        sonuc = bilgi("yok_plugin")
        assert "bulunamadi" in sonuc

    def test_bilgi_case_insensitive(self):
        from reymen.sistem.marketplace import bilgi

        sonuc = bilgi("TEST_PLUGIN")
        assert "test_plugin" in sonuc


class TestYukle:
    def test_yukle_plugin_bulunamadi(self):
        from reymen.sistem.marketplace import yukle

        sonuc = yukle("yok_plugin")
        assert "bulunamadi" in sonuc

    def test_yukle_zaten_yuklu(self, tmp_path):
        import reymen.sistem.marketplace as m

        # Plugin dizinini olustur (zaten yuklu)
        (m.PLUGIN_DIZINI / "test_plugin").mkdir(parents=True, exist_ok=True)
        sonuc = m.yukle("test_plugin")
        assert "zaten yuklu" in sonuc

    def test_yukle_kaynaksiz_plugin(self, monkeypatch, tmp_path):
        import reymen.sistem.marketplace as m

        kat = [
            {
                "ad": "kaynaksiz",
                "versiyon": "1.0",
                "aciklama": "no source",
                "kaynak": "",
                "yazar": "test",
                "lisans": "MIT",
                "etiketler": [],
                "bagimliliklar": [],
                "dokuman": "",
            }
        ]
        m.KATALOG_DOSYASI.write_text(json.dumps(kat), encoding="utf-8")
        sonuc = m.yukle("kaynaksiz")
        assert "kaynak URL belirtilmemis" in sonuc


class TestYukluMu:
    def test_yuklu_mi_var(self, tmp_path):
        import reymen.sistem.marketplace as m

        (m.PLUGIN_DIZINI / "mevcut_plugin").mkdir(parents=True, exist_ok=True)
        assert m._yuklu_mi("mevcut_plugin") is True

    def test_yuklu_mi_yok(self):
        from reymen.sistem.marketplace import _yuklu_mi

        assert _yuklu_mi("olmayan_plugin") is False


class TestMotorKaydet:
    def test_motor_kaydet(self):
        from reymen.sistem.marketplace import motor_kaydet

        class FakeMotor:
            _tools = {}

            def _plugin_arac_kaydet(self, ad, fn, desc):
                FakeMotor._tools[ad] = fn

        motor_kaydet(FakeMotor())
        assert "PLUGIN_MARKET_LISTE" in FakeMotor._tools
        assert "PLUGIN_MARKET_ARAMA" in FakeMotor._tools
        assert "PLUGIN_MARKET_YUKLE" in FakeMotor._tools
        assert "PLUGIN_MARKET_BILGI" in FakeMotor._tools

    def test_motor_kaydet_no_attr(self):
        from reymen.sistem.marketplace import motor_kaydet

        class FakeMotor:
            pass

        # Should not raise
        motor_kaydet(FakeMotor())


class TestVarsayilanYaml:
    def test_varsayilan_yaml_olustur(self, tmp_path):
        from reymen.sistem.marketplace import _varsayilan_yaml_olustur

        dizin = tmp_path / "test_plugin"
        dizin.mkdir()
        p = {
            "ad": "test_plugin",
            "versiyon": "2.0.0",
            "aciklama": "test desc",
            "yazar": "author",
            "lisans": "MIT",
        }
        _varsayilan_yaml_olustur(dizin, p)
        yaml_path = dizin / "plugin.yaml"
        assert yaml_path.exists()
        icerik = yaml_path.read_text(encoding="utf-8")
        assert "test_plugin" in icerik
        assert "2.0.0" in icerik


class TestMotoraKaydet:
    def test_motora_kaydet(self):
        from reymen.sistem.marketplace import _motora_kaydet

        # Should not raise
        _motora_kaydet("test_plugin")
