# -*- coding: utf-8 -*-
"""gateway/platforms/email.py — E-posta Platformu.

SMTP ile e-posta gonderir.
"""

import os
import smtplib
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



