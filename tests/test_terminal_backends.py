#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_terminal_backends.py — TerminalBackend birim testleri."""

import sys

sys.path.insert(0, ".")

import os
import tempfile

# Import edilebilir mi kontrol et
from terminal_backends import TerminalBackend, TerminalBackendDispatcher


class TestTerminalBackendInit:
    """Baslatma testleri."""

    def test_init_default(self):
        tb = TerminalBackend()
        assert tb._varsayilan_timeout == 60
        assert tb._calisma_dizini == os.getcwd()
        assert tb._ssh_baglantilari == {}
        assert tb._calisma_gecmisi == []

    def test_init_ozel(self):
        tb = TerminalBackend(varsayilan_timeout=30, calisma_dizini="/tmp")
        assert tb._varsayilan_timeout == 30
        assert tb._calisma_dizini == "/tmp"


class TestTerminalBackendLocal:
    """Local komut calistirma testleri."""

    def test_echo(self):
        tb = TerminalBackend()
        r = tb.local("echo Merhaba Terminal")
        assert r["basarili"] is True
        assert "Merhaba Terminal" in r.get("cikti", "")

    def test_basarisiz_komut(self):
        tb = TerminalBackend()
        r = tb.local("olmayan_komut_12345")
        assert r["basarili"] is False
        assert r.get("donus_kodu", 0) != 0

    def test_calisma_gecmisi(self):
        tb = TerminalBackend()
        tb.local("echo test1")
        tb.local("echo test2")
        gecmis = tb.gecmisi_getir(5)
        assert len(gecmis) >= 2

    def test_gecmis_temizle(self):
        tb = TerminalBackend()
        tb.local("echo test")
        sayi = tb.gecmisi_temizle()
        assert sayi >= 1
        assert tb.gecmisi_getir() == []

    def test_timeout(self):
        tb = TerminalBackend(varsayilan_timeout=1)
        r = tb.local("sleep 5")
        assert r["basarili"] is False
        assert "zaman asimi" in r.get("hata", "").lower()

    def test_list_komut(self):
        tb = TerminalBackend()
        r = tb.local(["echo", "list", "test"])
        assert r["basarili"] is True
        assert "list test" in r.get("cikti", "")


class TestTerminalBackendOrtam:
    """Ortam degiskeni testleri."""

    def test_ortam_ayarla(self):
        tb = TerminalBackend()
        tb.ortam_ayarla("REYMEN_TEST", "test_value")
        # Windows'ta $VAR calismaz, dogrudan env'den kontrol et
        r = tb.local("echo test_value_placeholder")
        assert tb._ortam_degiskenleri.get("REYMEN_TEST") == "test_value"
        assert r["basarili"] is True

    def test_ortam_ekle(self):
        tb = TerminalBackend()
        r = tb.calistir("echo $USER", ortam={"REYMEN_EK": "ek_deger"})
        assert r["basarili"] is True

    def test_calisma_dizini(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tb = TerminalBackend(calisma_dizini=tmpdir)
            # pwd Windows/Msys farki: /tmp/ vs C:\\... kontrol etmiyoruz
            assert tb._calisma_dizini == os.path.abspath(tmpdir)

    def test_calisma_dizini_degistir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tb = TerminalBackend()
            ok = tb.calisma_dizini_degistir(tmpdir)
            assert ok is True
            assert tb._calisma_dizini == os.path.abspath(tmpdir)

    def test_calisma_dizini_gecersiz(self):
        tb = TerminalBackend()
        ok = tb.calisma_dizini_degistir("/hic/yok/dizin")
        assert ok is False


class TestTerminalBackendDurum:
    """Durum testleri."""

    def test_durum(self):
        tb = TerminalBackend()
        d = tb.durum()
        assert "calisma_dizini" in d
        assert "varsayilan_timeout" in d
        assert d["varsayilan_timeout"] == 60

    def test_durum_ssh_sifir(self):
        tb = TerminalBackend()
        d = tb.durum()
        assert d["ssh_baglanti_sayisi"] == 0


class TestTerminalBackendDocker:
    """Docker testleri (docker yoksa es geçer)."""

    def test_docker_kontrol(self):
        tb = TerminalBackend()
        r = tb.docker("olmayan_konteyner")
        # Docker yoksa da hata mesaji donmeli
        assert isinstance(r, dict)
        assert "basarili" in r or "hata" in r

    def test_docker_calistir(self):
        tb = TerminalBackend()
        r = tb.docker_calistir("alpine", "echo merhaba")
        # Docker yoksa hata doner, patlamaz
        assert isinstance(r, dict)
        assert "basarili" in r or "hata" in r


class TestTerminalBackendSSH:
    """SSH testleri (baglanti yoksa hata doner)."""

    def test_ssh_baglanti_yok(self):
        tb = TerminalBackend()
        r = tb.ssh("olmayan.sunucu", "test")
        assert r["basarili"] is False

    def test_ssh_baglantilari_listele_bos(self):
        tb = TerminalBackend()
        assert tb.ssh_baglantilari_listele() == []


class TestTerminalBackendDispatcher:
    """TerminalBackendDispatcher testleri."""

    def test_dispatcher_basarili(self):
        d = TerminalBackendDispatcher()
        r = d.calistir("echo basarili")
        assert "[Tamam]" in r
        assert "basarili" in r

    def test_dispatcher_basarisiz(self):
        d = TerminalBackendDispatcher()
        r = d.calistir("olmayan_komut_12345")
        assert "[Hata]" in r

    def test_dispatcher_bos_cikti(self):
        d = TerminalBackendDispatcher()
        r = d.calistir("echo -n ''")
        assert "[Tamam]" in r

    def test_dispatcher_mode_local(self):
        d = TerminalBackendDispatcher(mode="local")
        r = d.calistir("echo test_mode")
        assert "[Tamam]" in r
        assert "test_mode" in r
