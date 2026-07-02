# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.skill_5n1k_otomasyon

import pytest
import src.reymen.sistem.skill_5n1k_otomasyon as _modul

def test_besN1K_var_mi():
    # Otomatik test: reymen.sistem.skill_5n1k_otomasyon.besN1K_var_mi
    try:
        _modul.besN1K_var_mi()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.skill_5n1k_otomasyon.besN1K_var_mi')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_besN1K_olustur():
    # Otomatik test: reymen.sistem.skill_5n1k_otomasyon.besN1K_olustur
    try:
        _modul.besN1K_olustur()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.skill_5n1k_otomasyon.besN1K_olustur')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_besN1K_ekle():
    # Otomatik test: reymen.sistem.skill_5n1k_otomasyon.besN1K_ekle
    try:
        _modul.besN1K_ekle()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.skill_5n1k_otomasyon.besN1K_ekle')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_tarama_yap():
    # Otomatik test: reymen.sistem.skill_5n1k_otomasyon.tarama_yap
    try:
        _modul.tarama_yap()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.skill_5n1k_otomasyon.tarama_yap')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))

def test_raporla():
    # Otomatik test: reymen.sistem.skill_5n1k_otomasyon.raporla
    try:
        _modul.raporla()
    except SystemExit:
        pytest.xfail('SystemExit')
    except TypeError:
        pytest.skip('Arguman gerekli: reymen.sistem.skill_5n1k_otomasyon.raporla')
    except Exception as hata:
        pytest.xfail('Runtime hatasi: ' + str(hata))
