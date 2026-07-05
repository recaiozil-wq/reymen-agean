# -*- coding: utf-8 -*-
"""firecrawl_tool.py â€” Firecrawl API: web scrape + search.

Firecrawl (api.firecrawl.dev/v1) kullanarak:
  - firecrawl_scrape(url) â†’ URL'nin markdown içeriÄŸini döndürür
  - firecrawl_search(query) â†’ web aramasÄ± yapar (SearchDispatcher'a yönlendirir)

API Key: FIRECRAWL_API_KEY env var'dan okunur.

Motor kayÄ±t:
    from reymen.arac.firecrawl_tool import motor_kaydet
    motor_kaydet(motor)

Not: Web arama iÅŸlevi artÄ±k reymen.arac.web_search_engine'deki
SearchDispatcher üzerinden yapÄ±lÄ±r. Bu dosya geriye uyumluluk için
korunmaktadÄ±r.
"""

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Optional

from reymen.arac.web_search_engine import _get_registry as _get_dispatcher

logger = logging.getLogger(__name__)

_API_BASE = "https://api.firecrawl.dev/v1"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
_TIMEOUT = 30


def _api_key() -> Optional[str]:
    """Firecrawl API key'i env var'dan oku."""
    key = os.environ.get("FIRECRAWL_API_KEY") or os.environ.get("FIRECRAWL_KEY")
    if key and not key.startswith("***"):
        return key
    return None


def _headers(api_key: Optional[str] = None) -> dict:
    """HTTP headers oluÅŸtur."""
    headers = {
        "User-Agent": _UA,
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def firecrawl_web_extract(url: str, format: str = "markdown") -> str:
    """Bir URL'nin içeriÄŸini Firecrawl ile çÄ±kar.

    Args:
        url: Ä°çeriÄŸi çÄ±karÄ±lacak URL
        format: Ã‡Ä±ktÄ± formatÄ± ('markdown' veya 'html')

    Returns:
        str: Sayfa içeriÄŸi (markdown/html) veya hata mesajÄ±
    """
    if not url or not url.strip():
        return "[FIRECRAWL] Hata: 'url' boÅŸ olamaz."

    url = url.strip()
    api_key = _api_key()

    body = json.dumps(
        {
            "url": url,
            "formats": [format],
            "onlyMainContent": True,
        }
    ).encode()

    req = urllib.request.Request(
        f"{_API_BASE}/scrape",
        data=body,
        headers=_headers(api_key),
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            sonuc = json.loads(resp.read().decode("utf-8"))

        if sonuc.get("success"):
            data = sonuc.get("data", {})
            icerik = (
                data.get(format, "")
                or data.get("markdown", "")
                or data.get("content", "")
            )
            metadata = data.get("metadata", {})
            baslik = metadata.get("title", "")
            kaynak_url = metadata.get("sourceURL", url)

            sonuc_metni = f"[Firecrawl Scrape]"
            if baslik:
                sonuc_metni += f"\nBaÅŸlÄ±k: {baslik}"
            sonuc_metni += f"\nURL: {kaynak_url}"
            sonuc_metni += f"\n\n{icerik}"
            return sonuc_metni
        else:
            hata = sonuc.get("error", "Bilinmeyen hata")
            return f"[FIRECRAWL] Scrape baÅŸarÄ±sÄ±z: {hata}"

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return "[FIRECRAWL] Kimlik doÄŸrulama hatasÄ±. FIRECRAWL_API_KEY env var'Ä±nÄ± kontrol edin."
        elif e.code == 402:
            return "[FIRECRAWL] Kredi limiti doldu. Firecrawl dashboard'dan kredi yükleyin."
        elif e.code == 429:
            return "[FIRECRAWL] Rate limit aÅŸÄ±ldÄ±. Daha sonra tekrar deneyin."
        return f"[FIRECRAWL] HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"[FIRECRAWL] BaÄŸlantÄ± hatasÄ±: {e.reason}"
    except Exception as e:
        logger.error("[FIRECRAWL] scrape hatasÄ±: %s", e)
        return f"[FIRECRAWL] Hata: {e}"


def firecrawl_web_search(query: str, max_results: int = 5, lang: str = "tr") -> str:
    """Firecrawl ile web aramasÄ± yap â€” SearchDispatcher'a yönlendirir.

    Args:
        query: Arama sorgusu
        max_results: Maksimum sonuç sayÄ±sÄ± (varsayÄ±lan: 5)
        lang: Dil kodu (varsayÄ±lan: 'tr')

    Returns:
        str: FormatlanmÄ±ÅŸ arama sonuçlarÄ±
    """
    # SearchDispatcher üzerinden firecrawl engine'i kullan
    dispatcher = _get_dispatcher()
    return dispatcher.ara(query, engine="firecrawl", max_sonuc=max_results)


def firecrawl_durum() -> str:
    """Firecrawl API durumunu kontrol et."""
    api_key = _api_key()
    if api_key:
        return "[FIRECRAWL] API key mevcut. HazÄ±r."
    return (
        "[FIRECRAWL] API key YOK. FIRECRAWL_API_KEY env var gerekli. "
        "https://firecrawl.dev'den key alÄ±n."
    )


# â”€â”€ Motor kayÄ±t â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def motor_kaydet(motor) -> None:
    """Firecrawl tool'larÄ±nÄ± motora kaydet.

    Kaydedilen tool'lar:
      - FIRECRAWL_SCRAPE: URL içeriÄŸi çÄ±kar (markdown)
      - FIRECRAWL_SEARCH: Web aramasÄ±
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    try:
        motor._plugin_arac_kaydet(
            "FIRECRAWL_SCRAPE",
            firecrawl_web_extract,
            "Firecrawl ile bir URL'nin içeriÄŸini markdown olarak çÄ±kar. "
            "Parametreler: url, format (varsayÄ±lan: markdown).",
        )
        motor._plugin_arac_kaydet(
            "FIRECRAWL_SEARCH",
            firecrawl_web_search,
            "Firecrawl ile web aramasÄ± yap. "
            "Parametreler: query, max_results (varsayÄ±lan: 5), lang (varsayÄ±lan: tr).",
        )
    except Exception as e:
        print(f"[Firecrawl] Motor kayÄ±t hatasÄ±: {e}")


# â”€â”€ KÄ±sa alias â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
firecrawl_web_extract = firecrawl_web_extract


if __name__ == "__main__":
    import sys

    print(firecrawl_durum())
    print()
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("http"):
            print(firecrawl_web_extract(arg))
        else:
            print(firecrawl_web_search(arg))
    else:
        print("KullanÄ±m: python firecrawl_tool.py <url|query>")
