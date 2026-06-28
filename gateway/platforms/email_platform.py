# -*- coding: utf-8 -*-
"""gateway/platforms/email_platform.py — E-posta Platformu.

SMTP ile e-posta gonderir.
Renamed from email.py to avoid stdlib `email` package shadowing.
"""

import os
import smtplib
import email as stdlib_email
from email.mime.text import MIMEText


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """E-posta gonder.

    Args:
        hedef: Alici e-posta adresi
        mesaj: E-posta icerigi
    """
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    from_addr = os.environ.get("SMTP_FROM", smtp_user)

    if not smtp_user or not smtp_pass:
        return "[Email]: SMTP kullanici/sifre ayarlanmamis."

    try:
        msg = MIMEText(mesaj[:10000], "plain", "utf-8")
        msg["Subject"] = f"ReYMeN Mesaji"
        msg["From"] = from_addr
        msg["To"] = hedef

        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return "[Email]: Mesaj gonderildi."
    except Exception as e:
        return f"[Email]: Hata: {e}"



class EmailAdapter:
    def __init__(self, config=None): self.platform="email"; self.config=config
    async def connect(self): return False
    async def disconnect(self): pass
    async def send(self, to, content, **kw):
        from gateway.platforms.base import SendResult
        return SendResult(success=False, error="Email not configured")
