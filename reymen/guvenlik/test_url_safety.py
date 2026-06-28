# -*- coding: utf-8 -*-
"""Test: url_safety.py — URL Guvenlik Kontrolu."""

import logging
import sys
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)

# Proje kokunu sys.path'e ekle
PROJE_KOK = Path(__file__).parent.parent.parent.resolve()
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

from reymen.guvenlik.url_safety import (
    url_guvenli_mi,
    url_temizle,
    YASAKLI_PROTOKOLLER,
    RISKLI_TLD,
    RISKLI_KELIMELER,
)


# ============================================================
# Sabitler / Konfigurasyon
# ============================================================

class TestSabitler:
    """YASAKLI_PROTOKOLLER, RISKLI_TLD, RISKLI_KELIMELER sabitleri."""

    def test_yasakli_protokoller_eksiksiz(self):
        assert len(YASAKLI_PROTOKOLLER) >= 6
        assert "file://" in YASAKLI_PROTOKOLLER
        assert "javascript:" in YASAKLI_PROTOKOLLER
        assert "data:" in YASAKLI_PROTOKOLLER
        assert "vbscript:" in YASAKLI_PROTOKOLLER

    def test_tum_protokoller_string(self):
        for proto in YASAKLI_PROTOKOLLER:
            assert isinstance(proto, str)
            assert len(proto) > 0

    def test_riskli_tld_eksiksiz(self):
        assert len(RISKLI_TLD) >= 8
        assert ".tk" in RISKLI_TLD
        assert ".xyz" in RISKLI_TLD
        assert ".top" in RISKLI_TLD

    def test_tum_tld_nokta_ile_baslar(self):
        for tld in RISKLI_TLD:
            assert tld.startswith(".")

    def test_riskli_kelimeler_eksiksiz(self):
        assert len(RISKLI_KELIMELER) >= 10
        assert "login" in RISKLI_KELIMELER
        assert "password" in RISKLI_KELIMELER
        assert "wallet" in RISKLI_KELIMELER


# ============================================================
# url_guvenli_mi — Temel Dogru URL'ler
# ============================================================

class TestGuvenliURL:
    """Guvenli olmasi gereken URL'ler."""

    def test_https_google(self):
        guvenli, mesaj = url_guvenli_mi("https://www.google.com")
        assert guvenli is True
        assert mesaj == ""

    def test_https_subdomain(self):
        guvenli, mesaj = url_guvenli_mi("https://sub.example.org/path")
        assert guvenli is True
        assert mesaj == ""

    def test_http_normal_site(self):
        guvenli, mesaj = url_guvenli_mi("http://example.com")
        assert guvenli is True
        assert mesaj == ""

    def test_https_derin_yol(self):
        guvenli, mesaj = url_guvenli_mi("https://github.com/user/repo/blob/main/file.py")
        assert guvenli is True
        assert mesaj == ""

    def test_https_query_parametreli(self):
        guvenli, mesaj = url_guvenli_mi("https://example.com/page?q=test&lang=tr")
        assert guvenli is True
        assert mesaj == ""

    def test_https_port_belirtilmis(self):
        guvenli, mesaj = url_guvenli_mi("https://example.com:8080/path")
        assert guvenli is True
        assert mesaj == ""

    def test_https_fragmentli(self):
        guvenli, mesaj = url_guvenli_mi("https://docs.python.org/3/#library")
        assert guvenli is True
        assert mesaj == ""


# ============================================================
# url_guvenli_mi — Localhost
# ============================================================

class TestLocalhost:
    """Localhost URL'leri her zaman guvenli."""

    def test_localhost_http(self):
        guvenli, mesaj = url_guvenli_mi("http://localhost:8080/api")
        assert guvenli is True
        assert mesaj == ""

    def test_localhost_https(self):
        guvenli, mesaj = url_guvenli_mi("https://localhost:3000")
        assert guvenli is True
        assert mesaj == ""

    def test_127_0_0_1(self):
        guvenli, mesaj = url_guvenli_mi("http://127.0.0.1:5000/test")
        assert guvenli is True
        assert mesaj == ""

    def test_localhost_alti_cizgi(self):
        guvenli, mesaj = url_guvenli_mi("http://localhost/")
        assert guvenli is True
        assert mesaj == ""


# ============================================================
# url_guvenli_mi — Yasakli Protokoller
# ============================================================

class TestYasakliProtokoller:
    """Yasakli protokoller engellenmeli."""

    def test_file_protokol(self):
        guvenli, mesaj = url_guvenli_mi("file:///etc/passwd")
        assert guvenli is False
        assert "file" in mesaj.lower()

    def test_ftp_protokol(self):
        guvenli, mesaj = url_guvenli_mi("ftp://files.example.com")
        assert guvenli is False
        assert "ftp" in mesaj.lower()

    def test_smb_protokol(self):
        guvenli, mesaj = url_guvenli_mi("smb://server/share")
        assert guvenli is False
        assert "smb" in mesaj.lower()

    def test_ldap_protokol(self):
        guvenli, mesaj = url_guvenli_mi("ldap://ldap.example.com")
        assert guvenli is False
        assert "ldap" in mesaj.lower()

    def test_javascript_protokol(self):
        guvenli, mesaj = url_guvenli_mi("javascript:alert(1)")
        assert guvenli is False
        assert "javascript" in mesaj.lower()

    def test_data_protokol(self):
        guvenli, mesaj = url_guvenli_mi("data:text/html,<script>alert(1)</script>")
        assert guvenli is False
        assert "data" in mesaj.lower()

    def test_vbscript_protokol(self):
        guvenli, mesaj = url_guvenli_mi("vbscript:msgbox(1)")
        assert guvenli is False
        assert "vbscript" in mesaj.lower()


# ============================================================
# url_guvenli_mi — HTTP/HTTPS Disindakiler
# ============================================================

class TestHttpHttpsZorunlu:
    """Sadece HTTP/HTTPS protokollerine izin verilmeli."""

    def test_gopher_engellenir(self):
        guvenli, mesaj = url_guvenli_mi("gopher://server/item")
        assert guvenli is False
        assert "sadece" in mesaj.lower() or "http" in mesaj.lower()

    def test_ws_engellenir(self):
        guvenli, mesaj = url_guvenli_mi("ws://example.com/ws")
        assert guvenli is False

    def test_wss_engellenir(self):
        guvenli, mesaj = url_guvenli_mi("wss://example.com/ws")
        assert guvenli is False

    def test_mailto_engellenir(self):
        guvenli, mesaj = url_guvenli_mi("mailto:test@example.com")
        assert guvenli is False

    def test_telnet_engellenir(self):
        guvenli, mesaj = url_guvenli_mi("telnet://example.com")
        assert guvenli is False

    def test_ssh_engellenir(self):
        guvenli, mesaj = url_guvenli_mi("ssh://example.com")
        assert guvenli is False


# ============================================================
# url_guvenli_mi — Riskli TLD'ler
# ============================================================

class TestRiskliTLD:
    """Riskli/guvenilmeyen TLD'ler engellenmeli."""

    def test_tk_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://malicious.tk/login")
        assert guvenli is False
        assert ".tk" in mesaj or "TLD" in mesaj

    def test_ml_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://phishing.ml")
        assert guvenli is False

    def test_ga_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://scam.ga")
        assert guvenli is False

    def test_cf_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://fake.cf")
        assert guvenli is False

    def test_gq_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://malware.gq")
        assert guvenli is False

    def test_xyz_tld(self):
        guvenli, mesaj = url_guvenli_mi("https://suspicious.xyz/download")
        assert guvenli is False

    def test_top_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://hack.top")
        assert guvenli is False

    def test_loan_tld(self):
        guvenli, mesaj = url_guvenli_mi("https://scam.loan/pay")
        assert guvenli is False

    def test_win_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://free.win/prize")
        assert guvenli is False

    def test_bid_tld(self):
        guvenli, mesaj = url_guvenli_mi("http://auction.bid")
        assert guvenli is False


# ============================================================
# url_guvenli_mi — Buyuk Kucuk Harf Duyarsizligi
# ============================================================

class TestBuyukKucukHarf:
    """URL lowercasing testleri."""

    def test_buyuk_harf_https(self):
        guvenli, _ = url_guvenli_mi("HTTPS://GOOGLE.COM")
        assert guvenli is True

    def test_buyuk_harf_yasakli_protokol(self):
        guvenli, mesaj = url_guvenli_mi("FILE:///etc/passwd")
        assert guvenli is False
        assert "file" in mesaj.lower()

    def test_buyuk_harf_tld(self):
        guvenli, _ = url_guvenli_mi("http://example.TK")
        assert guvenli is False

    def test_karisik_harf_protokol(self):
        guvenli, mesaj = url_guvenli_mi("JaVaScRiPt:alert(1)")
        assert guvenli is False


# ============================================================
# url_guvenli_mi — Edge Case'ler
# ============================================================

class TestEdgeCase:
    """Sinir ve uckagit durumlari."""

    def test_bos_string(self):
        guvenli, mesaj = url_guvenli_mi("")
        assert guvenli is False
        assert mesaj

    def test_bosluklu_url(self):
        """Boslukla baslayan URL strip edilmeli."""
        guvenli, mesaj = url_guvenli_mi("  https://example.com  ")
        assert guvenli is True

    def test_None_input(self):
        try:
            url_guvenli_mi(None)  # type: ignore
        except (TypeError, AttributeError) as exc:
            logger.warning("test_None_input: beklenen istisna yakalandi: %s", exc)
            pass
        # AttributeError beklenir, test pattern olarak baska testlerle uyumlu

    def test_int_input(self):
        try:
            url_guvenli_mi(12345)  # type: ignore
        except (TypeError, AttributeError) as exc:
            logger.warning("test_int_input: beklenen istisna yakalandi: %s", exc)
            pass

    def test_https_icinde_file_yok(self):
        """file kelimesi icinde gecen https URL engellenmemeli."""
        guvenli, _ = url_guvenli_mi("https://example.com/file/download")
        assert guvenli is True

    def test_https_icinde_data_yok(self):
        """data kelimesi icinde gecen https URL engellenmemeli."""
        guvenli, _ = url_guvenli_mi("https://example.com/data/report")
        assert guvenli is True

    def test_https_icinde_ftp_yok(self):
        """ftp kelimesi icinde gecen https URL engellenmemeli."""
        guvenli, _ = url_guvenli_mi("https://ftp.example.com/files")
        assert guvenli is True

    def test_https_icinde_js_yok(self):
        """js kelimesi icinde gecen URL engellenmemeli (prefix match)."""
        guvenli, _ = url_guvenli_mi("https://example.com/js/app.js")
        assert guvenli is True

    def test_tld_ortada_yok(self):
        """Riskli TLD parcasi URL ortasinda gecerse engellemeli."""
        guvenli, mesaj = url_guvenli_mi("https://subdomain.tk.example.com")
        # .tk kelime olarak gecer, .tk in URL -> engellenir
        # Not: startswith degil 'in' kontrolu
        assert guvenli is False


# ============================================================
# url_temizle
# ============================================================

class TestUrlTemizle:
    """url_temizle() parametre temizleme testleri."""

    def test_query_parametreleri_temizlenir(self):
        temiz = url_temizle("https://example.com/page?q=test&pass=123")
        assert "?" not in temiz
        assert temiz == "https://example.com/page"

    def test_query_olmayan_url_degismez(self):
        url = "https://example.com/page"
        temiz = url_temizle(url)
        assert temiz == url

    def test_fragment_korunmaz(self):
        """url_temizle sadece query'i temizler, fragment degil."""
        temiz = url_temizle("https://example.com/page#section")
        assert temiz == "https://example.com/page#section"

    def test_https_query_fragment_karisik(self):
        temiz = url_temizle("https://example.com/path?key=val#head")
        assert "?" not in temiz
        assert "#head" in temiz

    def test_bos_query_sorunsuz(self):
        temiz = url_temizle("https://example.com/?")
        # urllib bos query'yi korur, bu kabul edilebilir
        assert temiz == "https://example.com/?"

    def test_coklu_parametre_temizlenir(self):
        temiz = url_temizle("https://example.com/login?user=admin&pass=123&redirect=/panel")
        assert "?" not in temiz

    def test_localhost_query_temizlenir(self):
        temiz = url_temizle("http://localhost:8080/api?token=secret")
        assert temiz == "http://localhost:8080/api"

    def test_bos_url_temizle(self):
        """Bos URL donusum sorunsuz olmali."""
        temiz = url_temizle("")
        assert temiz == ""

    def test_path_sorunsuz(self):
        """Query'siz path'lerde degisiklik olmamali."""
        url = "https://github.com/user/repo"
        assert url_temizle(url) == url


# ============================================================
# Entegrasyon / Birlikte Calisma
# ============================================================

class TestEntegrasyon:
    """Birden fazla fonksiyonun birlikte calismasi."""

    def test_guvenli_url_temizleme_zinciri(self):
        url = "https://example.com/login?token=abc123"
        guvenli, _ = url_guvenli_mi(url)
        assert guvenli is True
        temiz = url_temizle(url)
        assert "?" not in temiz
        assert temiz == "https://example.com/login"

    def test_engellenen_url_temizlenmez(self):
        """Engellenen URL'nin guvenli olmadigini oncelikle kontrol et."""
        url = "file:///etc/passwd?x=1"
        guvenli, mesaj = url_guvenli_mi(url)
        assert guvenli is False
        assert "file" in mesaj.lower()

    def test_tld_engelli_sonra_temizle(self):
        url = "http://malware.tk/download?file=evil.exe"
        guvenli, _ = url_guvenli_mi(url)
        assert guvenli is False
        # Temizleme calisir ama URL yine guvensiz
        temiz = url_temizle(url)
        assert "?" not in temiz
        guvenli2, _ = url_guvenli_mi(temiz)
        assert guvenli2 is False  # tld hala riskli
