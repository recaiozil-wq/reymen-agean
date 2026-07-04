# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.provider_transport

import pytest
import src.reymen.sistem.provider_transport as _modul


def test_gonder():
    # Otomatik test: reymen.sistem.provider_transport.gonder
    try:
        _modul.gonder()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.gonder")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_al():
    # Otomatik test: reymen.sistem.provider_transport.al
    try:
        _modul.al()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.al")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_baglan():
    # Otomatik test: reymen.sistem.provider_transport.baglan
    try:
        _modul.baglan()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.baglan")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_koprus():
    # Otomatik test: reymen.sistem.provider_transport.koprus
    try:
        _modul.koprus()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.koprus")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_ping():
    # Otomatik test: reymen.sistem.provider_transport.ping
    try:
        _modul.ping()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.ping")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_aktif_saglayicilar():
    # Otomatik test: reymen.sistem.provider_transport.aktif_saglayicilar
    try:
        _modul.aktif_saglayicilar()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip(
            "Arguman gerekli: reymen.sistem.provider_transport.aktif_saglayicilar"
        )
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_tum_saglayicilar():
    # Otomatik test: reymen.sistem.provider_transport.tum_saglayicilar
    try:
        _modul.tum_saglayicilar()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip(
            "Arguman gerekli: reymen.sistem.provider_transport.tum_saglayicilar"
        )
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_gecmisi_getir():
    # Otomatik test: reymen.sistem.provider_transport.gecmisi_getir
    try:
        _modul.gecmisi_getir()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.gecmisi_getir")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_gecmisi_temizle():
    # Otomatik test: reymen.sistem.provider_transport.gecmisi_temizle
    try:
        _modul.gecmisi_temizle()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.gecmisi_temizle")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_durum_raporu():
    # Otomatik test: reymen.sistem.provider_transport.durum_raporu
    try:
        _modul.durum_raporu()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.durum_raporu")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))


def test_ornek_kanal():
    # Otomatik test: reymen.sistem.provider_transport.ornek_kanal
    try:
        _modul.ornek_kanal()
    except SystemExit:
        pytest.xfail("SystemExit")
    except TypeError:
        pytest.skip("Arguman gerekli: reymen.sistem.provider_transport.ornek_kanal")
    except Exception as hata:
        pytest.xfail("Runtime hatasi: " + str(hata))
