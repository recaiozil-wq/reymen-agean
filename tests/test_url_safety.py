# -*- coding: utf-8 -*-
"""Tests for url_safety — URL security validation."""
import pytest
from reymen.guvenlik.url_safety import url_guvenli_mi, url_temizle, YASAKLI_PROTOKOLLER, RISKLI_TLD


class TestUrlGuvenliMi:
    """url_guvenli_mi() tests."""

    # ── Safe URLs ──

    @pytest.mark.parametrize("url", [
        "https://www.google.com",
        "https://github.com/user/repo",
        "https://docs.python.org/3/library/",
        "http://localhost:8080",
        "http://127.0.0.1:3000/api",
        "https://example.com/path?q=hello",
    ])
    def test_safe_urls_pass(self, url):
        guvenli, _ = url_guvenli_mi(url)
        assert guvenli is True

    # ── Blocked protocols ──

    @pytest.mark.parametrize("proto", [
        "file:///etc/passwd",
        "ftp://evil.com/steal",
        "smb://network/share",
        "ldap://dc.example.com",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "vbscript:MsgBox(1)",
    ])
    def test_blocked_protocols(self, proto):
        guvenli, mesaj = url_guvenli_mi(proto)
        assert guvenli is False
        assert "yasakli" in mesaj.lower() or "protokol" in mesaj.lower()

    # ── Non-HTTP(S) URLs ──

    @pytest.mark.parametrize("url", [
        "smtp://mail.example.com",
        "telnet://server",
        "custom://something",
    ])
    def test_non_http_blocked(self, url):
        guvenli, mesaj = url_guvenli_mi(url)
        assert guvenli is False
        assert "HTTP" in mesaj

    # ── Risky TLDs ──

    @pytest.mark.parametrize("url", [
        "https://phish.tk/login",
        "https://malware.ml/download",
        "https://scam.ga/get",
        "https://free.xyz/offer",
        "https://cheap.top/buy",
    ])
    def test_risky_tld_blocked(self, url):
        guvenli, mesaj = url_guvenli_mi(url)
        assert guvenli is False
        assert "TLD" in mesaj

    # ── Localhost always allowed ──

    @pytest.mark.parametrize("url", [
        "http://localhost:8080/admin",
        "https://localhost/api",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000/secret",
    ])
    def test_localhost_always_safe(self, url):
        guvenli, _ = url_guvenli_mi(url)
        assert guvenli is True

    # ── Whitespace handling ──

    def test_strips_whitespace(self):
        guvenli, _ = url_guvenli_mi("  https://google.com  ")
        assert guvenli is True

    def test_case_insensitive(self):
        guvenli, _ = url_guvenli_mi("FILE:///etc/passwd")
        assert guvenli is False


class TestUrlTemizle:
    """url_temizle() tests."""

    def test_removes_query_params(self):
        result = url_temizle("https://example.com/path?token=abc&session=xyz")
        assert "token=" not in result
        assert "session=" not in result
        assert "example.com/path" in result

    def test_no_query_unchanged(self):
        url = "https://example.com/page"
        assert url_temizle(url) == url

    def test_preserves_fragment(self):
        url = "https://example.com/page#section"
        result = url_temizle(url)
        assert "example.com/page" in result


class TestConstants:
    """Module constants sanity checks."""

    def test_blocked_protocols_non_empty(self):
        assert len(YASAKLI_PROTOKOLLER) >= 6

    def test_risky_tld_non_empty(self):
        assert len(RISKLI_TLD) >= 5

    def test_javascript_in_blocked(self):
        assert "javascript:" in YASAKLI_PROTOKOLLER

    def test_data_in_blocked(self):
        assert "data:" in YASAKLI_PROTOKOLLER
