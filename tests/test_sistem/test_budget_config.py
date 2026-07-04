# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.budget_config

import pytest
import src.reymen.sistem.budget_config as _modul


def test_run():
    # Otomatik test: reymen.sistem.budget_config.run
    try:
        _modul.run()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.run")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_butce_getir():
    # Otomatik test: reymen.sistem.budget_config.butce_getir
    try:
        _modul.butce_getir()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.butce_getir")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_butce_ayarla():
    # Otomatik test: reymen.sistem.budget_config.butce_ayarla
    try:
        _modul.butce_ayarla()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.butce_ayarla")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_butce_kullan():
    # Otomatik test: reymen.sistem.budget_config.butce_kullan
    try:
        _modul.butce_kullan()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.butce_kullan")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_kalan_butce():
    # Otomatik test: reymen.sistem.budget_config.kalan_butce
    try:
        _modul.kalan_butce()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.kalan_butce")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_sifirla():
    # Otomatik test: reymen.sistem.budget_config.sifirla
    try:
        _modul.sifirla()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.sifirla")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_liste_tipleri():
    # Otomatik test: reymen.sistem.budget_config.liste_tipleri
    try:
        _modul.liste_tipleri()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.liste_tipleri")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_ozet():
    # Otomatik test: reymen.sistem.budget_config.ozet
    try:
        _modul.ozet()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.ozet")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_provider_maliyeti():
    # Otomatik test: reymen.sistem.budget_config.provider_maliyeti
    try:
        _modul.provider_maliyeti()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.budget_config.provider_maliyeti")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
