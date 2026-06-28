# -*- coding: utf-8 -*-
"""tools/web_search.py — Web Arama Araci.

WEB_ARA icin requests ile basit web arama ve sayfa getirme.
"""

import requests


def ara(sorgu: str) -> str:
    """Web'de ara (basit HTTP get).

    Args:
        sorgu: Arama sorgusu veya URL

    Returns:
        Sayfa icerigi
    """
    if not sorgu:
        return "[Web]: Sorgu gerekli."

    # URL mi yoksa arama sorgusu mu?
    if sorgu.startswith("http"):
        url = sorgu
    else:
        url = f"https://www.google.com/search?q={sorgu.replace(' ', '+')}"

    try:
        r = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0"
        })
        if r.status_code == 200:
            import re
            metin = r.text
            metin = re.sub(r'<[^>]+>', ' ', metin)
            metin = re.sub(r'\s+', ' ', metin).strip()
            return f"[Web] {len(metin)} karakter:\n{metin[:2000]}"
        return f"[Web]: HTTP {r.status_code}"
    except requests.Timeout:
        return "[Web]: Zaman asimi."
    except Exception as e:
        return f"[Web]: Hata: {e}"


def ping() -> bool:
    try:
        r = requests.get("https://google.com", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


if __name__ == "__main__":
    print(ara("example.com"))
