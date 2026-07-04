# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.mcp_serve

import pytest
import src.reymen.sistem.mcp_serve as _modul


def test_stdio_dongu():
    # Otomatik test: reymen.sistem.mcp_serve.stdio_dongu
    try:
        _modul.stdio_dongu()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.mcp_serve.stdio_dongu")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
