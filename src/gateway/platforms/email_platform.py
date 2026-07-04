# -*- coding: utf-8 -*-
"""Email platform — SMTP-based email adapter."""

from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from typing import Optional


# ── Module-level state ──────────────────────────────────────────────────────

_aktif = False


# ── Result class ────────────────────────────────────────────────────────────


@dataclass
class SendResult:
    success: bool
    error: str = ""


# ── Functions ───────────────────────────────────────────────────────────────


def baslat():
    global _aktif
    _aktif = True
    return None


def durdur():
    global _aktif
    _aktif = False
    return None


def mesaj_gonder(to: str, msg: str) -> str:
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_from = os.environ.get("SMTP_FROM", "")

    if not smtp_user or not smtp_pass:
        return "SMTP kullanici/sifre ayarlanmamis"

    if not smtp_from:
        smtp_from = smtp_user

    try:
        mime = MIMEText(msg, "plain", "utf-8")
        mime["Subject"] = "ReYMeN Message"
        mime["From"] = smtp_from
        mime["To"] = to

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [to], mime.as_string())
        return "Email gonderildi"
    except Exception as e:
        return f"Hata: {e}"


# ── Adapter class ───────────────────────────────────────────────────────────


class EmailAdapter:
    """Email platform adaptörü."""

    platform = "email"

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._baglandi = False

    async def connect(self) -> bool:
        return False

    def disconnect(self):
        self._baglandi = False

    async def send(self, to: str, message: str) -> SendResult:
        return SendResult(success=False, error="not configured")
