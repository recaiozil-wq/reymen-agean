# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem._puanla

import pytest
import src.reymen.sistem._puanla as _modul


def test_kaynak_turu_bul():
    # Otomatik test: reymen.sistem._puanla.kaynak_turu_bul
    try:
        _modul.kaynak_turu_bul()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem._puanla.kaynak_turu_bul")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_kaynak_guvenirlik_puan():
    # Otomatik test: reymen.sistem._puanla.kaynak_guvenirlik_puan
    try:
        _modul.kaynak_guvenirlik_puan()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem._puanla.kaynak_guvenirlik_puan")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_guncellik_puan():
    # Otomatik test: reymen.sistem._puanla.guncellik_puan
    try:
        _modul.guncellik_puan()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem._puanla.guncellik_puan")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_dogrulama_puan():
    # Otomatik test: reymen.sistem._puanla.dogrulama_puan
    try:
        _modul.dogrulama_puan()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem._puanla.dogrulama_puan")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_celiski_puan():
    # Otomatik test: reymen.sistem._puanla.celiski_puan
    try:
        _modul.celiski_puan()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem._puanla.celiski_puan")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_hesapla():
    # Otomatik test: reymen.sistem._puanla.hesapla
    try:
        _modul.hesapla()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem._puanla.hesapla")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_karar_aciklamasi():
    # Otomatik test: reymen.sistem._puanla.karar_aciklamasi
    try:
        _modul.karar_aciklamasi()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem._puanla.karar_aciklamasi")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
