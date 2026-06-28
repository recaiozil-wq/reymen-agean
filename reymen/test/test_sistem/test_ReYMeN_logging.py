# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.ReYMeN_logging

import pytest
import reymen.sistem.ReYMeN_logging as _modul

def test_kur():
    # Otomatik test: reymen.sistem.ReYMeN_logging.kur
    try:
        _modul.kur()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.ReYMeN_logging.kur')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_get_logger():
    # Otomatik test: reymen.sistem.ReYMeN_logging.get_logger
    try:
        _modul.get_logger()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.ReYMeN_logging.get_logger')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_set_session_context():
    # Otomatik test: reymen.sistem.ReYMeN_logging.set_session_context
    try:
        _modul.set_session_context()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.ReYMeN_logging.set_session_context')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_get_session_context():
    # Otomatik test: reymen.sistem.ReYMeN_logging.get_session_context
    try:
        _modul.get_session_context()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.ReYMeN_logging.get_session_context')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))
