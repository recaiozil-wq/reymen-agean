# -*- coding: utf-8 -*-
"""error_classifier.py için pytest testleri."""

from __future__ import annotations

from pathlib import Path
import sys

# Proje kökünü sys.path'e ekle
_proje_kok = Path(__file__).resolve().parent.parent
if str(_proje_kok) not in sys.path:
    sys.path.insert(0, str(_proje_kok))

import pytest
from error_classifier import ErrorClassifier


# ── Fixture ──────────────────────────────────────────────────────────────


@pytest.fixture
def classifier() -> ErrorClassifier:
    """Test için hazır ErrorClassifier örneği."""
    return ErrorClassifier()


# ── _metne_cevir (convert to string) ─────────────────────────────────────


class TestMetneCevir:
    """_metne_cevir metodunun doğru çalıştığını test eder."""

    def test_str_hata_dogrudan_gecer(self, classifier: ErrorClassifier):
        """String girdi aynen döndürülmeli."""
        assert classifier._metne_cevir("bir hata") == "bir hata"

    def test_exception_nesnesi_isim_ve_mesaj_icerir(self, classifier: ErrorClassifier):
        """Exception nesnesi 'Type: mesaj' formatında döndürülmeli."""
        exc = ValueError("gecersiz değer")
        sonuc = classifier._metne_cevir(exc)
        assert "ValueError: gecersiz değer" in sonuc

    def test_exception_sadece_tip(self, classifier: ErrorClassifier):
        """Exception'ın mesajı boş olsa bile tip adı gelmeli."""
        exc = RuntimeError()
        sonuc = classifier._metne_cevir(exc)
        assert sonuc.startswith("RuntimeError:")

    def test_int_sayiya_cevrilir(self, classifier: ErrorClassifier):
        """int gibi tipler str() ile dönüştürülmeli."""
        assert classifier._metne_cevir(404) == "404"


# ── _kategori_bul (category matching) ────────────────────────────────────


class TestKategoriBul:
    """Kategori eşleştirme mantığını test eder."""

    def test_import_kategorisi_module_not_found(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("ModuleNotFoundError: No module named 'flask'")
            == "import"
        )

    def test_import_kategorisi_import_error(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("ImportError: cannot import name X") == "import"

    def test_syntax_kategorisi(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("SyntaxError: invalid syntax on line 5")
            == "syntax"
        )

    def test_indentation_error_syntax_kategorisi(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("IndentationError: unexpected indent") == "syntax"
        )

    def test_dizin_kategorisi_file_not_found(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("FileNotFoundError: config.yaml bulunamadi")
            == "dizin"
        )

    def test_dizin_kategorisi_not_found_metni(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("hata: dosya not found") == "dizin"

    def test_baglanti_kategorisi_connection_error(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("ConnectionRefusedError: sunucu kapali")
            == "baglanti"
        )

    def test_baglanti_kategorisi_ecnrefused(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("ECONNREFUSED: 127.0.0.1:8080") == "baglanti"

    def test_api_kategorisi_401(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("HTTP 401: Unauthorized") == "api"

    def test_api_kategorisi_403(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("403 Forbidden") == "api"

    def test_api_kategorisi_api_key(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("API key gecersiz") == "api"

    def test_tip_kategorisi_type_error(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("TypeError: unsupported operand type(s)") == "tip"
        )

    def test_tip_kategorisi_value_error(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("ValueError: invalid literal for int()") == "tip"
        )

    def test_izin_kategorisi(self, classifier: ErrorClassifier):
        assert (
            classifier._kategori_bul("PermissionError: [Errno 13] izin yok") == "izin"
        )

    def test_zaman_asimi_kategorisi(self, classifier: ErrorClassifier):
        # "baglanti" / "Bağlantı" kelimeleri baglanti kategorisini tetikler,
        # bu yüzden nötr bir mesaj kullanıyoruz
        assert (
            classifier._kategori_bul("TimeoutError: islem zaman asimi") == "zaman_asimi"
        )

    def test_timed_out_kelimesi(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("Connection timed out") == "zaman_asimi"

    def test_tanimlanamayan_hata_diger_kategorisi(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("Beklenmedik bir hata olustu") == "diger"

    def test_bos_string_diger_kategorisi(self, classifier: ErrorClassifier):
        assert classifier._kategori_bul("") == "diger"

    def test_buyuk_kucuk_harf_duyarli_degil(self, classifier: ErrorClassifier):
        """Kategori eşleştirme case-insensitive olmalı."""
        assert classifier._kategori_bul("syntaxerror: invalid syntax") == "syntax"
        # "ModuleNotFoundError" case-insensitive: "not found" aynı zamanda dizin desenidir,
        # bu yüzden "module not found" değil, "import" ile başlayan tür adı kullanıyoruz
        assert classifier._kategori_bul("importerror: no module named 'x'") == "import"


# ── _cozum_olustur (solution generation) ─────────────────────────────────


class TestCozumOlustur:
    """Çözüm önerisi oluşturma mantığını test eder."""

    def test_cozum_import_temel(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("import", "ImportError: bir hata")
        assert "pip install" in cozum

    def test_cozum_import_paket_adi_cikarilir(self, classifier: ErrorClassifier):
        """No module named 'X' deseninden paket adı çıkarılmalı."""
        cozum = classifier._cozum_olustur(
            "import",
            "ModuleNotFoundError: No module named 'requests'",
        )
        assert cozum == "pip install requests"

    def test_cozum_import_noktali_paket_adi(self, classifier: ErrorClassifier):
        """Noktalı modül adından ana paket çıkarılmalı."""
        cozum = classifier._cozum_olustur(
            "import",
            "ModuleNotFoundError: No module named 'flask.ext.sqlalchemy'",
        )
        assert cozum == "pip install flask"

    def test_cozum_syntax(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("syntax", "SyntaxError: ...")
        assert "söz dizimi" in cozum

    def test_cozum_dizin(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("dizin", "FileNotFoundError: ...")
        assert "yolunu kontrol" in cozum

    def test_cozum_baglanti(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("baglanti", "ConnectionError: ...")
        assert "Ağ bağlantısı" in cozum

    def test_cozum_api_429_rate_limit(self, classifier: ErrorClassifier):
        """429 hatasına özel çözüm üretilmeli."""
        cozum = classifier._cozum_olustur("api", "HTTP 429: Too Many Requests")
        assert "Rate limit" in cozum

    def test_cozum_api_diger(self, classifier: ErrorClassifier):
        """API 429 dışındaki durumlar genel API çözümünü döndürmeli."""
        cozum = classifier._cozum_olustur("api", "HTTP 401: Unauthorized")
        assert "API anahtarını" in cozum

    def test_cozum_tip(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("tip", "TypeError: ...")
        assert "Değişken tipini" in cozum

    def test_cozum_izin(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("izin", "PermissionError: ...")
        assert "izinlerini kontrol" in cozum

    def test_cozum_zaman_asimi(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("zaman_asimi", "TimeoutError: ...")
        assert "Zaman aşımı" in cozum

    def test_cozum_diger(self, classifier: ErrorClassifier):
        cozum = classifier._cozum_olustur("diger", "bilinmeyen hata")
        assert "traceback" in cozum

    def test_cozum_bilinmeyen_kategori(self, classifier: ErrorClassifier):
        """KATEGORILER'de olmayan bir kategori için varsayılan çözüm."""
        cozum = classifier._cozum_olustur("bilinmeyen", "bir hata")
        assert cozum == "Hata mesajını incele"


# ── siniflandir (main API) ───────────────────────────────────────────────


class TestSiniflandir:
    """Ana siniflandir metodunun entegre çalışmasını test eder."""

    def test_tam_akis_str_girdi(self, classifier: ErrorClassifier):
        sonuc = classifier.siniflandir("ImportError: No module named 'pandas'")
        assert sonuc["kategori"] == "import"
        assert sonuc["cozum"] == "pip install pandas"
        assert "No module named" in sonuc["mesaj"]

    def test_tam_akis_exception_girdi(self, classifier: ErrorClassifier):
        exc = FileNotFoundError("config.json bulunamadi")
        sonuc = classifier.siniflandir(exc)
        assert sonuc["kategori"] == "dizin"
        assert "yolunu kontrol" in sonuc["cozum"]
        assert "FileNotFoundError" in sonuc["mesaj"]

    def test_mesaj_200_karakterle_sinirli(self, classifier: ErrorClassifier):
        uzun_hata = "x" * 500
        sonuc = classifier.siniflandir(uzun_hata)
        assert len(sonuc["mesaj"]) <= 200

    def test_donus_anahtarlari_tutarlidir(self, classifier: ErrorClassifier):
        sonuc = classifier.siniflandir("baglanti hatasi")
        assert set(sonuc.keys()) == {"kategori", "cozum", "mesaj"}

    def test_api_429_rate_limit_cozumu(self, classifier: ErrorClassifier):
        """429 için özel çözüm üretilmeli."""
        sonuc = classifier.siniflandir("HTTP 429: Too Many Requests (API rate limit)")
        assert sonuc["kategori"] == "api"
        assert "Rate limit" in sonuc["cozum"]

    def test_bos_hata_diger_kategorisi(self, classifier: ErrorClassifier):
        sonuc = classifier.siniflandir("")
        assert sonuc["kategori"] == "diger"

    @pytest.mark.parametrize(
        "hata_metni,beklenen_kategori",
        [
            ("ModuleNotFoundError: No module named 'foo'", "import"),
            ("SyntaxError: invalid syntax", "syntax"),
            ("FileNotFoundError: x", "dizin"),
            ("ConnectionError: x", "baglanti"),
            ("HTTP 403: Forbidden", "api"),
            ("TypeError: x", "tip"),
            ("PermissionError: x", "izin"),
            ("TimeoutError: x", "zaman_asimi"),
            ("BilinmeyenHata: xyz", "diger"),
        ],
    )
    def test_parametrik_kategoriler(
        self, classifier: ErrorClassifier, hata_metni: str, beklenen_kategori: str
    ):
        sonuc = classifier.siniflandir(hata_metni)
        assert sonuc["kategori"] == beklenen_kategori

    @pytest.mark.parametrize(
        "hata_metni,beklenen_paket",
        [
            ("No module named 'numpy'", "numpy"),
            ("No module named 'django.core'", "django"),
        ],
    )
    def test_no_module_named_cozumu(
        self, classifier: ErrorClassifier, hata_metni: str, beklenen_paket: str
    ):
        sonuc = classifier.siniflandir(f"ImportError: {hata_metni}")
        assert sonuc["cozum"] == f"pip install {beklenen_paket}"
