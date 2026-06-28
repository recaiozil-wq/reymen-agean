# -*- coding: utf-8 -*-
"""tools/browser_cdp_tool.py — Chrome DevTools Protocol Araci.

Chrome/Chromium tarayicisina CDP uzerinden baglanir,
konsol, DOM, ag ve performans bilgisi alir.
"""

import os
import json
import requests


def cdp_baglan(port: int = 9222) -> str:
    """Chrome DevTools'a baglan.

    Args:
        port: Chrome remote debugging port

    Returns:
        Baglanti durumu
    """
    try:
        r = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return f"[CDP] Baglandi: {data.get('Browser', '?')} (ws://{data.get('webSocketDebuggerUrl', '')[:30]}...)"
        return f"[CDP] Hata {r.status_code}"
    except requests.ConnectionError:
        return "[CDP] Baglanti yok. Chrome'u --remote-debugging-port=9222 ile baslat."
    except Exception as e:
        return f"[CDP] Hata: {e}"


def cdp_sekmeleri_listele(port: int = 9222) -> str:
    """Acik sekmeleri listele."""
    try:
        r = requests.get(f"http://127.0.0.1:{port}/json", timeout=5)
        if r.status_code == 200:
            sekmeler = r.json()
            satirlar = [f"[CDP] {len(sekmeler)} sekme:\n"]
            for s in sekmeler[:10]:
                satirlar.append(f"  {s.get('title', '?')[:40]} ({s.get('url', '?')[:40]})")
            return "\n".join(satirlar)
        return f"[CDP] Hata {r.status_code}"
    except Exception as e:
        return f"[CDP] Hata: {e}"


def run(port: int = 9222, action: str = "connect") -> str:
    """Browser CDP aracinin genel run() wrapper'ı."""
    if action == "connect":
        return cdp_baglan(port)
    if action == "list":
        return cdp_sekmeleri_listele(port)
    return f"[CDP]: Bilinmeyen action: {action}. Desteklenen: connect, list"


if __name__ == "__main__":
    print(cdp_baglan())
    print(cdp_sekmeleri_listele())
