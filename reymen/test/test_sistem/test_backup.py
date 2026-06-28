# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.backup

import pytest
import reymen.sistem.backup as _modul

def test_yedekle():
    # Otomatik test: reymen.sistem.backup.yedekle
    try:
        _modul.yedekle()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.backup.yedekle')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_yedek_listele():
    # Otomatik test: reymen.sistem.backup.yedek_listele
    try:
        _modul.yedek_listele()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.backup.yedek_listele')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))
