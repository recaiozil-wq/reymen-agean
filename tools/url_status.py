# -*- coding: utf-8 -*-
"""url_status.py — URL durum kontrolü aracı.

Belirtilen URL'nin HTTP durum kodunu ve yanıt süresini ölçer.
"""

import json
import time

# Opsiyonel: requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Fallback: urllib
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


TOOL_META = {
    "aciklama": "URL'nin HTTP durum kodunu ve yanıt süresini kontrol eder.",
    "parametreler": [
        {"ad": "url", "tip": "str", "aciklama": "Kontrol edilecek URL."},
        {"ad": "timeout", "tip": "int", "aciklama": "Zaman aşımı saniyesi (varsayılan: 5)."},
    ],
    "ornek": 'URL_STATUS("https://ornek.com", timeout=10)',
    "kategori": "web",
}


def run(url: str = "", timeout: int = 5, *args, **kwargs) -> str:
    """URL durumunu kontrol et.

    Args:
        url: Kontrol edilecek URL.
        timeout: Zaman aşımı saniyesi.

    Returns:
        JSON: durum kodu, yanıt süresi, header bilgisi.
    """
    if not url:
        return json.dumps({"hata": "url parametresi zorunludur."}, ensure_ascii=False)

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    baslangic = time.time()

    try:
        if HAS_REQUESTS:
            resp = requests.head(url, timeout=timeout, headers={
                "User-Agent": "ReYMeN/1.0",
            })
            sure = round(time.time() - baslangic, 3)
            return json.dumps({
                "url": url,
                "durum": "ulastirilabilir" if resp.ok else "hata",
                "status_code": resp.status_code,
                "yanit_suresi_sn": sure,
                "content_type": resp.headers.get("Content-Type", ""),
                "server": resp.headers.get("Server", ""),
                "content_length": resp.headers.get("Content-Length", ""),
            }, ensure_ascii=False, indent=2)
        elif HAS_URLLIB:
            req = Request(url, method="HEAD", headers={"User-Agent": "ReYMeN/1.0"})
            try:
                with urlopen(req, timeout=timeout) as resp:
                    sure = round(time.time() - baslangic, 3)
                    return json.dumps({
                        "url": url,
                        "durum": "ulastirilabilir",
                        "status_code": resp.status,
                        "yanit_suresi_sn": sure,
                        "content_type": resp.headers.get("Content-Type", ""),
                    }, ensure_ascii=False, indent=2)
            except HTTPError as e:
                sure = round(time.time() - baslangic, 3)
                return json.dumps({
                    "url": url,
                    "durum": "hata",
                    "status_code": e.code,
                    "yanit_suresi_sn": sure,
                }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"hata": "HTTP kutuphanesi bulunamadi."}, ensure_ascii=False)
    except Exception as e:
        sure = round(time.time() - baslangic, 3)
        return json.dumps({
            "url": url,
            "durum": "hatali",
            "status_code": None,
            "yanit_suresi_sn": sure,
            "hata": str(e),
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("=== URL DURUM ===")
    print(run("https://httpbin.org/status/200", timeout=10))
    print("\n=== HATALI URL ===")
    print(run("https://olmayan-site-123456789.com", timeout=3))
