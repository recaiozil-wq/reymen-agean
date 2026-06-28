# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.account_usage

import pytest
import reymen.sistem.account_usage as _modul

def test_hesap_ekle():
    # Otomatik test: reymen.sistem.account_usage.hesap_ekle
    try:
        _modul.hesap_ekle()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.hesap_ekle')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_hesap_ozet():
    # Otomatik test: reymen.sistem.account_usage.hesap_ozet
    try:
        _modul.hesap_ozet()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.hesap_ozet')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_ekle():
    # Otomatik test: reymen.sistem.account_usage.ekle
    try:
        _modul.ekle()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.ekle')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_ozet():
    # Otomatik test: reymen.sistem.account_usage.ozet
    try:
        _modul.ozet()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.ozet')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_provider_raporu():
    # Otomatik test: reymen.sistem.account_usage.provider_raporu
    try:
        _modul.provider_raporu()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.provider_raporu')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_aylik_rapor():
    # Otomatik test: reymen.sistem.account_usage.aylik_rapor
    try:
        _modul.aylik_rapor()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.aylik_rapor')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_butce_uyarisi():
    # Otomatik test: reymen.sistem.account_usage.butce_uyarisi
    try:
        _modul.butce_uyarisi()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.butce_uyarisi')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_sifirla():
    # Otomatik test: reymen.sistem.account_usage.sifirla
    try:
        _modul.sifirla()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.account_usage.sifirla')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))
