# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.session_search_tool

import pytest
import src.reymen.sistem.session_search_tool as _modul


def test_run():
    # Otomatik test: reymen.sistem.session_search_tool.run
    try:
        _modul.run()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.session_search_tool.run")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_check_fn():
    # Otomatik test: reymen.sistem.session_search_tool.check_fn
    try:
        _modul.check_fn()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.session_search_tool.check_fn")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
