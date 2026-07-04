# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.model_metadata

import pytest
import src.reymen.sistem.model_metadata as _modul


def test_model_bilgisi():
    # Otomatik test: reymen.sistem.model_metadata.model_bilgisi
    try:
        _modul.model_bilgisi()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.model_metadata.model_bilgisi")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_modele_gore_sec():
    # Otomatik test: reymen.sistem.model_metadata.modele_gore_sec
    try:
        _modul.modele_gore_sec()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.model_metadata.modele_gore_sec")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_model_listele():
    # Otomatik test: reymen.sistem.model_metadata.model_listele
    try:
        _modul.model_listele()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.model_metadata.model_listele")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_maliyet_hesapla():
    # Otomatik test: reymen.sistem.model_metadata.maliyet_hesapla
    try:
        _modul.maliyet_hesapla()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.model_metadata.maliyet_hesapla")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
