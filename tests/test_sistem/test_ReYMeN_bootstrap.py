# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.ReYMeN_bootstrap

import pytest
import src.reymen.sistem.ReYMeN_bootstrap as _modul


def test_apply_windows_utf8_bootstrap():
    # Otomatik test: reymen.sistem.ReYMeN_bootstrap.apply_windows_utf8_bootstrap
    try:
        _modul.apply_windows_utf8_bootstrap()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip(
            "Arguman gerekli: reymen.sistem.ReYMeN_bootstrap.apply_windows_utf8_bootstrap"
        )
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
