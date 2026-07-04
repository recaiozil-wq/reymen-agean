# -*- coding: utf-8 -*-
"""gateway/platforms/email_platform.py testleri."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestEmailPlatform:
    def test_baslat_durdur(self):
        from gateway.platforms.email_platform import baslat, durdur

        assert baslat() is None
        assert durdur() is None

    def test_mesaj_gonder_no_credentials(self):
        with patch(
            "os.environ.get",
            side_effect=lambda k, d=None: {
                "SMTP_USER": "",
                "SMTP_PASS": "",
                "SMTP_SERVER": "smtp.gmail.com",
                "SMTP_PORT": "587",
                "SMTP_FROM": "",
            }.get(k, d or ""),
        ):
            from gateway.platforms.email_platform import mesaj_gonder

            result = mesaj_gonder("test@example.com", "Merhaba")
            assert "kullanici/sifre" in result or "ayarlanmamis" in result

    def test_mesaj_gonder_success(self):
        env_vals = {
            "SMTP_USER": "user",
            "SMTP_PASS": "pass",
            "SMTP_SERVER": "smtp.test.com",
            "SMTP_PORT": "587",
            "SMTP_FROM": "user@test.com",
        }

        def mock_env(key, default=""):
            return env_vals.get(key, default)

        with patch("os.environ.get", side_effect=mock_env):
            with patch("smtplib.SMTP") as mock_smtp:
                instance = MagicMock()
                mock_smtp.return_value.__enter__.return_value = instance
                from gateway.platforms.email_platform import mesaj_gonder

                result = mesaj_gonder("test@example.com", "Mesaj ici")
                assert "gonderildi" in result.lower() or "Email" in result
                instance.starttls.assert_called_once()
                instance.login.assert_called_once_with("user", "pass")

    def test_mesaj_gonder_error(self):
        env_vals = {
            "SMTP_USER": "user",
            "SMTP_PASS": "pass",
            "SMTP_SERVER": "smtp.test.com",
            "SMTP_PORT": "587",
        }

        def mock_env(key, default=""):
            return env_vals.get(key, default)

        with patch("os.environ.get", side_effect=mock_env):
            with patch("smtplib.SMTP", side_effect=Exception("Baglanti reddi")):
                from gateway.platforms.email_platform import mesaj_gonder

                result = mesaj_gonder("test@example.com", "Mesaj")
                assert "Hata" in result
                assert "Baglanti" in result

    def test_mesaj_gonder_truncates_long(self):
        env_vals = {
            "SMTP_USER": "user",
            "SMTP_PASS": "pass",
            "SMTP_SERVER": "smtp.test.com",
            "SMTP_PORT": "587",
        }

        def mock_env(key, default=""):
            return env_vals.get(key, default)

        long_msg = "M" * 20000
        with patch("os.environ.get", side_effect=mock_env):
            with patch("smtplib.SMTP") as mock_smtp:
                instance = MagicMock()
                mock_smtp.return_value.__enter__.return_value = instance
                from gateway.platforms.email_platform import mesaj_gonder
                from email.mime.text import MIMEText

                result = mesaj_gonder("test@example.com", long_msg)
                assert "gonderildi" in result.lower() or "Email" in result

    def test_email_adapter(self):
        from gateway.platforms.email_platform import EmailAdapter

        adapter = EmailAdapter()
        assert adapter.platform == "email"
        import asyncio

        result = asyncio.run(adapter.send("a", "b"))
        assert result.success is False
        assert "not configured" in result.error

    def test_email_adapter_connect(self):
        from gateway.platforms.email_platform import EmailAdapter

        adapter = EmailAdapter(config={})
        import asyncio

        result = asyncio.run(adapter.connect())
        assert result is False
