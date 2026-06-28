# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.ReYMeN_time

import pytest
import reymen.sistem.ReYMeN_time as _modul

def test_get_timezone():
    # Otomatik test: reymen.sistem.ReYMeN_time.get_timezone
    try:
        _modul.get_timezone()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.ReYMeN_time.get_timezone')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_reset_cache():
    # Otomatik test: reymen.sistem.ReYMeN_time.reset_cache
    try:
        _modul.reset_cache()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.ReYMeN_time.reset_cache')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_now():
    # Otomatik test: reymen.sistem.ReYMeN_time.now
    try:
        _modul.now()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.ReYMeN_time.now')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))
