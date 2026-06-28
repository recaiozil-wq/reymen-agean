# -*- coding: utf-8 -*-
"""plugins/dashboard_auth/self_hosted.py — Self-hosted kimlik doğrulama."""
import os


class SelfHostedAuthProvider:
    """Self-hosted token tabanlı kimlik doğrulama."""

    def __init__(self, token: str = ''):
        self.token = token or os.environ.get('DASHBOARD_TOKEN', '')

    def verify(self, token: str) -> bool:
        return bool(self.token) and token == self.token


def is_configured() -> bool:
    return bool(os.environ.get('DASHBOARD_TOKEN'))


if __name__ == '__main__':
    print('SelfHostedAuthProvider importlandı.')
