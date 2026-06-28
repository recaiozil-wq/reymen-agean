# -*- coding: utf-8 -*-
"""plugins/dashboard_auth/basic.py — Basit HTTP kimlik doğrulama."""
import base64, os


class BasicAuthProvider:
    """Kullanıcı adı/şifre kimlik doğrulama."""

    def __init__(self, username: str = '', password: str = ''):
        self.username = username or os.environ.get('DASHBOARD_USERNAME', 'admin')
        self.password = password or os.environ.get('DASHBOARD_PASSWORD', '')

    def verify(self, credentials: str) -> bool:
        try:
            decoded = base64.b64decode(credentials).decode()
            u, p = decoded.split(':', 1)
            return u == self.username and p == self.password
        except Exception:
            return False


def is_configured() -> bool:
    return bool(os.environ.get('DASHBOARD_PASSWORD'))


if __name__ == '__main__':
    print('BasicAuthProvider importlandı.')
