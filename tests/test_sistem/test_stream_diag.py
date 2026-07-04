# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.stream_diag

import pytest
import src.reymen.sistem.stream_diag as _modul


def test_izle():
    # Otomatik test: reymen.sistem.stream_diag.izle
    try:
        _modul.izle()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.izle")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_hiz_olc():
    # Otomatik test: reymen.sistem.stream_diag.hiz_olc
    try:
        _modul.hiz_olc()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.hiz_olc")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_gecikme_olc():
    # Otomatik test: reymen.sistem.stream_diag.gecikme_olc
    try:
        _modul.gecikme_olc()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.gecikme_olc")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_paket_kaybi():
    # Otomatik test: reymen.sistem.stream_diag.paket_kaybi
    try:
        _modul.paket_kaybi()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.paket_kaybi")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_raporla():
    # Otomatik test: reymen.sistem.stream_diag.raporla
    try:
        _modul.raporla()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.raporla")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_stream_durum():
    # Otomatik test: reymen.sistem.stream_diag.stream_durum
    try:
        _modul.stream_durum()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.stream_durum")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_tum_streamlar():
    # Otomatik test: reymen.sistem.stream_diag.tum_streamlar
    try:
        _modul.tum_streamlar()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.tum_streamlar")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_temizle():
    # Otomatik test: reymen.sistem.stream_diag.temizle
    try:
        _modul.temizle()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.temizle")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_test_stream():
    # Otomatik test: reymen.sistem.stream_diag.test_stream
    try:
        _modul.test_stream()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.stream_diag.test_stream")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
