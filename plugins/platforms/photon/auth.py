# -*- coding: utf-8 -*-
"""plugins/platforms/photon/auth.py — Photon kimlik doğrulama."""
from __future__ import annotations

import os


def is_configured() -> bool:
    """Photon yapılandırıp yapılandırılmadığını kontrol et."""
    return bool(os.environ.get("BLUEBUBBLES_PASSWORD"))


def get_server_url() -> str:
    return os.environ.get("BLUEBUBBLES_SERVER_URL", "")


def get_password() -> str:
    return os.environ.get("BLUEBUBBLES_PASSWORD", "")


if __name__ == "__main__":
    print("photon.auth importlandı. Yapılandırıldı:", is_configured())
