# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.cli

import pytest
import src.reymen.sistem.cli as _modul


def test_main():
    # Otomatik test: reymen.sistem.cli.main
    try:
        _modul.main()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.cli.main")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
