# -*- coding: utf-8 -*-
"""tools/yuanbao_tools.py — Yuanbao Gruptan Mesaj Atma Araci.

Yuanbao gruplarina otomatik mesaj gonderme.
"""

import os
import requests


def yuanbao_gonder(grup_kodu: str, mesaj: str) -> str:
    """Yuanbao grubuna mesaj gonder.

    Args:
        grup_kodu: Grup kodu
        mesaj: Mesaj icerigi

    Returns:
        Durum mesaji
    """
    token = os.environ.get("YUANBAO_TOKEN", "")
    if not token or token.startswith("***"):
        return "[Yuanbao]: YUANBAO_TOKEN ayarlanmamis."

    try:
        r = requests.post(
            f"https://api.yuanbao.cn/v1/groups/{grup_kodu}/messages",
            json={"content": mesaj[:2000]},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if r.status_code == 200:
            return "[Yuanbao]: Mesaj gonderildi."
        return f"[Yuanbao]: Hata {r.status_code}"
    except Exception as e:
        return f"[Yuanbao]: Hata: {e}"


if __name__ == "__main__":
    print(yuanbao_gonder("test", "merhaba"))
