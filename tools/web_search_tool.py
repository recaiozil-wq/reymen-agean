# -*- coding: utf-8 -*-
"""web_search_tool.py — Web arama (DuckDuckGo)."""

import urllib.request
import urllib.parse
import json


_TIMEOUT = 8
_DDG_API = "https://api.duckduckgo.com/"
_MAX_LEN = 500


def _temiz_kes(metin: str, limit: int = _MAX_LEN) -> str:
    """Cümle ortasında kesmez; son boşluğa snap eder."""
    if len(metin) <= limit:
        return metin
    kesim = metin[:limit].rfind(" ")
    return metin[: kesim if kesim > 0 else limit] + "…"


def _ddg_ara(sorgu: str) -> str:
    params = urllib.parse.urlencode({
        "q": sorgu,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1",
    })
    url = f"{_DDG_API}?{params}"

    with urllib.request.urlopen(url, timeout=_TIMEOUT) as r:
        # r.read() → bytes; açıkça decode et
        data = json.loads(r.read().decode("utf-8"))

    # 1. Tercih: doğrudan özet
    abstract = data.get("AbstractText", "").strip()
    if abstract:
        kaynak = data.get("AbstractURL", "")
        satir = f"🔍 {_temiz_kes(abstract)}"
        if kaynak:
            satir += f"\nKaynak: {kaynak}"
        return satir

    # 2. Fallback: RelatedTopics — nested Topics da taranır
    topics = data.get("RelatedTopics", [])
    for item in topics:
        if not isinstance(item, dict):
            continue
        # Düz topic
        if "Text" in item:
            return f"🔍 {_temiz_kes(item['Text'])}"
        # Nested Topics listesi
        for sub in item.get("Topics", []):
            if isinstance(sub, dict) and "Text" in sub:
                return f"🔍 {_temiz_kes(sub['Text'])}"

    return "[Sonuc] Bulunamadi."


def run(sorgu: str = "", kaynak: str = "duckduckgo") -> str:
    sorgu = sorgu.strip()
    if not sorgu:
        return "[Hata]: sorgu parametresi gerekli."

    if kaynak == "duckduckgo":
        try:
            return _ddg_ara(sorgu)
        except urllib.error.URLError as e:
            return f"[Hata]: Ağ hatası — {e.reason}"
        except json.JSONDecodeError:
            return "[Hata]: DuckDuckGo geçersiz JSON döndürdü."
        except Exception as e:
            return f"[Hata]: {e}"

    return f"[Hata]: Bilinmeyen kaynak '{kaynak}'. Geçerli: duckduckgo"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("WEB_ARAMA", run, "Web'de ara (DuckDuckGo)")
