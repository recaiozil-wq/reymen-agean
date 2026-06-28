# -*- coding: utf-8 -*-
"""
araclar_web.py — Web arama + sayfa icerik cekme (cok kaynakli, dayanikli).

Provider zinciri (sirali fallback):
  1. Brave Search  — BRAVE_API_KEY varsa
  2. SearXNG       — SEARXNG_URL varsa (kendi instance)
  3. DuckDuckGo HTML scrape
  4. DuckDuckGo Lite scrape

Sayfa icerik cekme:
  - Playwright varsa headless Chromium
  - Yoksa urllib + HTML stripping

API anahtari gerekmez (DDG fallback her zaman calisir).
"""
import html
import json
import os
import re
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
_HEADERS = {"User-Agent": _UA}


# ── Yardimci ──────────────────────────────────────────────────────────────────

def _temizle(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def _http_get(url: str, params: dict = None, headers: dict = None,
              timeout: int = 15) -> str:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={**_HEADERS, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        charset = r.headers.get_content_charset("utf-8") or "utf-8"
        return r.read().decode(charset, errors="replace")


def _http_post(url: str, veri: dict, headers: dict = None, timeout: int = 15) -> str:
    body = urllib.parse.urlencode(veri).encode()
    req  = urllib.request.Request(
        url, data=body,
        headers={**_HEADERS, "Content-Type": "application/x-www-form-urlencoded",
                 **(headers or {})}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        charset = r.headers.get_content_charset("utf-8") or "utf-8"
        return r.read().decode(charset, errors="replace")


def _sonuc_formatla(sonuclar: list, kaynak: str) -> str:
    if not sonuclar:
        return ""
    satirlar = [f"[Web Arama — {kaynak}]:"]
    for baslik, url, ozet in sonuclar:
        parca = f"- {baslik}"
        if ozet:
            parca += f"\n  {ozet[:180]}"
        parca += f"\n  {url[:120]}"
        satirlar.append(parca)
    return "\n".join(satirlar)


# ── Provider 1: Brave Search ──────────────────────────────────────────────────

def _brave_ara(sorgu: str, adet: int) -> list | None:
    api_key = os.environ.get("BRAVE_API_KEY", "").strip()
    if not api_key or api_key.startswith("***"):
        return None
    try:
        metin = _http_get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": sorgu, "count": adet, "safesearch": "off"},
            headers={"Accept": "application/json",
                     "Accept-Encoding": "gzip",
                     "X-Subscription-Token": api_key},
        )
        veri = json.loads(metin)
        web  = veri.get("web", {}).get("results", [])
        return [(r.get("title", ""), r.get("url", ""),
                 r.get("description", "")) for r in web[:adet]]
    except Exception:
        return None


# ── Provider 2: SearXNG ───────────────────────────────────────────────────────

def _searxng_ara(sorgu: str, adet: int) -> list | None:
    base_url = os.environ.get("SEARXNG_URL", "").strip().rstrip("/")
    if not base_url:
        return None
    try:
        metin = _http_get(
            f"{base_url}/search",
            params={"q": sorgu, "format": "json", "pageno": 1},
        )
        veri = json.loads(metin)
        sonuclar = veri.get("results", [])
        return [(r.get("title", ""), r.get("url", ""),
                 r.get("content", "")) for r in sonuclar[:adet]]
    except Exception:
        return None


# ── Provider 3: DuckDuckGo HTML ───────────────────────────────────────────────

def _ddg_html(sorgu: str, adet: int) -> list | None:
    try:
        r = _http_post("https://html.duckduckgo.com/html/", {"q": sorgu})
        bloklar = re.findall(
            r'result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?result__snippet[^>]*>(.*?)</a>',
            r, re.DOTALL,
        )
        return [(_temizle(b), _temizle(l), _temizle(o))
                for l, b, o in bloklar[:adet]] or None
    except Exception:
        return None


# ── Provider 4: DuckDuckGo Lite ───────────────────────────────────────────────

def _ddg_lite(sorgu: str, adet: int) -> list | None:
    try:
        r = _http_get("https://lite.duckduckgo.com/lite/", params={"q": sorgu})
        linkler = re.findall(
            r'<a[^>]*class="result-link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            r, re.DOTALL,
        )
        return [(_temizle(b), _temizle(l), "")
                for l, b in linkler[:adet]] or None
    except Exception:
        return None


# ── Firecrawl (API key gerekli) ───────────────────────────────────────────────

def _firecrawl_sonuc(sorgu: str, adet: int = 5) -> list | None:
    """Firecrawl API ile web araması — Brave/DDG formatında list döndürür."""
    api_key = os.environ.get("FIRECRAWL_API_KEY") or os.environ.get("FIRECRAWL_KEY")
    if not api_key or api_key.startswith("***"):
        return None
    try:
        url = "https://api.firecrawl.dev/v1/search"
        data = json.dumps({"query": sorgu, "maxResults": adet, "lang": "tr"}).encode()
        req = urllib.request.Request(
            url, data=data,
            headers={**_HEADERS, "Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            sonuc = json.loads(r.read().decode())
        if "data" in sonuc and "results" in sonuc["data"]:
            return [(r.get("title", ""), r.get("url", ""),
                     r.get("description", "") or r.get("content", "")[:300])
                    for r in sonuc["data"]["results"][:adet]]
        return None
    except Exception:
        return None


# ── Ana arama fonksiyonu ──────────────────────────────────────────────────────

PROVIDERLAR = [
    ("Firecrawl", _firecrawl_sonuc),
    ("Brave",   _brave_ara),
    ("SearXNG", _searxng_ara),
    ("DDG-HTML", _ddg_html),
    ("DDG-Lite", _ddg_lite),
]


def web_ara(sorgu: str, adet: int = 5) -> str:
    """Internette arar. Providerlar siraliyla denenir, ilk basaranin sonucu doner."""
    for isim, fn in PROVIDERLAR:
        try:
            sonuclar = fn(sorgu, adet)
            if sonuclar:
                return _sonuc_formatla(sonuclar, isim)
        except Exception:
            continue
    return "[Web Arama]: Hicbir provider sonuc vermedi. Internet baglantisini kontrol et."


# ── Sayfa icerik cekme ────────────────────────────────────────────────────────

def web_icerik_al(url: str, max_karakter: int = 3000) -> str:
    """Bir URL'nin metin icerigini cekin. Playwright > urllib fallback."""
    # Playwright dene
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            p = b.new_page()
            p.goto(url, timeout=20000, wait_until="domcontentloaded")
            baslik = p.title()
            metin  = p.inner_text("body")[:max_karakter]
            b.close()
        return f"[Sayfa] {baslik}\nURL: {url}\n\n{metin}"
    except Exception as _araclar__e178:
        print(f"[UYARI] araclar_web.py:179 - {_araclar__e178}")

    # urllib fallback
    try:
        from html.parser import HTMLParser
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            charset = r.headers.get_content_charset("utf-8") or "utf-8"
            icerik  = r.read().decode(charset, errors="replace")

        class _P(HTMLParser):
            def __init__(self):
                super().__init__()
                self._t = []
                self._atla = False
            def handle_starttag(self, t, _):
                if t in ("script", "style", "nav", "footer"):
                    self._atla = True
            def handle_endtag(self, t):
                if t in ("script", "style", "nav", "footer"):
                    self._atla = False
            def handle_data(self, d):
                if not self._atla and d.strip():
                    self._t.append(d.strip())

        p = _P()
        p.feed(icerik)
        metin = " ".join(p._t)[:max_karakter]
        return f"[Sayfa:urllib] URL: {url}\n\n{metin}"
    except Exception as e:
        return f"[Web] Icerik alinamadi: {e}"


# ── Motor kayit ───────────────────────────────────────────────────────────────

def motor_kaydet(motor) -> None:
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    try:
        motor._plugin_arac_kaydet(
            "WEB_ARA",
            lambda ham="": web_ara(
                re.findall(r'"((?:[^"\\]|\\.)*)"', ham)[0]
                if re.findall(r'"((?:[^"\\]|\\.)*)"', ham) else ham.strip('"')
            ),
            "DuckDuckGo / Brave ile internet araması yap",
        )
        motor._plugin_arac_kaydet(
            "WEB_ICERIK",
            lambda ham="": web_icerik_al(
                re.findall(r'"((?:[^"\\]|\\.)*)"', ham)[0]
                if re.findall(r'"((?:[^"\\]|\\.)*)"', ham) else ham.strip('"')
            ),
            "Bir URL'nin metin icerigini al",
        )
    except Exception as e:
        print(f"[WebArama] Motor kayit hatasi: {e}")


if __name__ == "__main__":
    import sys
    sorgu = sys.argv[1] if len(sys.argv) > 1 else "python asyncio nedir"
    print(web_ara(sorgu, adet=3))
