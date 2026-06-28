"""Test reymen.core.ogrenme — SQLite hafıza, TTL, imza, doğrulama."""
import pytest


@pytest.fixture(autouse=True)
def _temp_db(monkeypatch, tmp_path):
    """Her testte geçici DB kullan."""
    db_path = tmp_path / "test_hafiza.db"
    monkeypatch.setattr("reymen.core.ogrenme.DB_PATH", db_path)
    from reymen.core import ogrenme
    ogrenme.tablo_olustur()
    yield
    if db_path.exists():
        db_path.unlink()


def _hata_uret(msg: str = "name 'x' is not defined") -> Exception:
    """Gerçek Exception objesi üret (traceback ile)."""
    try:
        raise NameError(msg)
    except NameError as e:
        return e


def _value_error_uret(msg: str = "invalid literal") -> Exception:
    """Farklı tip Exception üret."""
    try:
        raise ValueError(msg)
    except ValueError as e:
        return e


class TestImzaUret:
    def test_imza_uret_kararli(self):
        from reymen.core.ogrenme import imza_uret
        s1 = imza_uret(_hata_uret("name 'x' is not defined"))
        s2 = imza_uret(_hata_uret("name 'x' is not defined"))
        assert s1 == s2

    def test_imza_uret_farkli_hata(self):
        from reymen.core.ogrenme import imza_uret
        # Farklı exception tipleri farklı imza üretmeli
        s1 = imza_uret(_hata_uret("name 'x' is not defined"))
        s2 = imza_uret(_value_error_uret("invalid literal"))
        assert s1 != s2

    def test_imza_uret_sha256(self):
        from reymen.core.ogrenme import imza_uret
        imza = imza_uret(_hata_uret("unsupported operand"))
        # 16 karakter hex (sha256[:16])
        assert len(imza) == 16
        assert all(c in "0123456789abcdef" for c in imza)


class TestCozumKaydetVeBul:
    def test_kaydet_ve_bul(self):
        from reymen.core.ogrenme import cozum_kaydet, cozum_bul, imza_uret
        imza = imza_uret(_hata_uret("name 'x' is not defined"))
        cozum_kaydet(
            imza=imza,
            hata_tipi="NameError",
            hata_ozet="name 'x' is not defined",
            cozum_kodu="x = 1",
            kaynak_script="test.py",
            basarili=True,
        )
        sonuc = cozum_bul(imza)
        assert sonuc == "x = 1"

    def test_bul_yok(self):
        from reymen.core.ogrenme import cozum_bul
        sonuc = cozum_bul("olmayan_imza")
        assert sonuc is None


class TestIstatistik:
    def test_istatistik_bos(self):
        from reymen.core.ogrenme import istatistik
        s = istatistik()
        assert s["toplam"] == 0
        assert s["basarili"] == 0

    def test_istatistik_dolu(self):
        from reymen.core.ogrenme import cozum_kaydet, istatistik, imza_uret
        imza = imza_uret(_hata_uret("test"))
        cozum_kaydet(imza=imza, hata_tipi="NameError", hata_ozet="test",
                     cozum_kodu="x=1", kaynak_script="t.py", basarili=True)
        s = istatistik()
        assert s["toplam"] == 1


class TestBackoff:
    def test_backoff_bekle(self):
        from reymen.core.ogrenme import backoff_bekle
        # 1. deneme: 1s
        assert backoff_bekle(1) == 1.0
        # 2. deneme: 2s
        assert backoff_bekle(2) == 2.0
        # 3. deneme: 4s
        assert backoff_bekle(3) == 4.0

    def test_backoff_max(self):
        from reymen.core.ogrenme import backoff_bekle, RETRY_MAX_BEKLEME
        # Çok yüksek deneme → max ile sınırlı
        assert backoff_bekle(100) <= RETRY_MAX_BEKLEME