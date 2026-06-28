# -*- coding: utf-8 -*-
"""url_fetcher.py — URL'den içerik çekme aracı.

Belirtilen URL'den HTTP GET ile içerik alır.
"""

import json

# Opsiyonel: requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Fallback: urllib (built-in)
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


TOOL_META = {
    "aciklama": "Belirtilen URL'den HTTP GET ile içerik çeker.",
    "parametreler": [
        {"ad": "url", "tip": "str", "aciklama": "İçerik çekilecek URL."},
        {"ad": "timeout", "tip": "int", "aciklama": "Zaman aşımı saniyesi (varsayılan: 10)."},
    ],
    "ornek": 'URL_FETCHER("https://api.example.com/veri", timeout=15)',
    "kategori": "web",
}


def run(url: str = "", timeout: int = 10, *args, **kwargs) -> str:
    """URL'den içerik çek.

    Args:
        url: İçerik çekilecek URL.
        timeout: Zaman aşımı saniyesi (varsayılan: 10).

    Returns:
        JSON: içerik, durum kodu, header bilgisi.
    """
    if not url:
        return json.dumps({"hata": "url parametresi zorunludur."}, ensure_ascii=False)

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        if HAS_REQUESTS:
            resp = requests.get(url, timeout=timeout, headers={
                "User-Agent": "ReYMeN/1.0",
                "Accept": "text/html,application/json,*/*",
            })
            icerik = resp.text[:50000]
            return json.dumps({
                "durum": "basarili",
                "status_code": resp.status_code,
                "content_type": resp.headers.get("Content-Type", ""),
                "boyut_bytes": len(icerik.encode("utf-8")),
                "icerik": icerik,
                "header": dict(resp.headers),
            }, ensure_ascii=False, indent=2)
        elif HAS_URLLIB:
            req = Request(url, headers={"User-Agent": "ReYMeN/1.0"})
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read(100000)
                icerik = raw.decode("utf-8", errors="replace")
                return json.dumps({
                    "durum": "basarili",
                    "status_code": resp.status,
                    "content_type": resp.headers.get("Content-Type", ""),
                    "boyut_bytes": len(raw),
                    "icerik": icerik[:50000],
                }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "hata": "Ne requests ne de urllib kullanilamiyor."
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "hata": f"URL cekme hatasi: {str(e)}"
        }, ensure_ascii=False)


if __name__ == "__main__":
    print("=== URL CEK (ornek) ===")
    print(run("https://httpbin.org/get", timeout=10))
