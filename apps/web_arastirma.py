# -*- coding: utf-8 -*-
"""
apps/web_arastirma.py — Web Arastirma Uygulamasi.

Araçlar:
  ara(sorgu)          — DuckDuckGo Lite JSON arama
  url_oku(url)        — Ham HTML → metin (BeautifulSoup yoksa fallback)
  ozet_al(url)        — URL iceriği kisa ozet (LLM gerektirir)

CLI:
    python apps/web_arastirma.py ara "Python asyncio"
    python apps/web_arastirma.py url "https://example.com"
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent


def ara(sorgu: str, limit: int = 5) -> dict:
    """DuckDuckGo Instant Answer API ile arama."""
    url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode({
        "q": sorgu, "format": "json", "no_html": "1", "skip_disambig": "1"
    })
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ReYMeNAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())

        sonuclar = []
        # Abstract (Wikipedia gibi)
        if data.get("AbstractText"):
            sonuclar.append({
                "baslik": data.get("Heading", sorgu),
                "url": data.get("AbstractURL", ""),
                "ozet": data["AbstractText"][:300],
            })
        # Related Topics
        for t in data.get("RelatedTopics", [])[:limit]:
            if isinstance(t, dict) and t.get("Text") and t.get("FirstURL"):
                sonuclar.append({
                    "baslik": t["Text"][:80],
                    "url": t["FirstURL"],
                    "ozet": t["Text"][:200],
                })
        return {"sorgu": sorgu, "sonuclar": sonuclar[:limit]}
    except Exception as e:
        return {"sorgu": sorgu, "hata": str(e), "sonuclar": []}


def url_oku(url: str, max_karakter: int = 3000) -> dict:
    """URL'den ham metin al."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 ReYMeNAgent/1.0"
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            ham = r.read()
            kodlama = r.headers.get_content_charset("utf-8")
            try:
                html = ham.decode(kodlama, errors="replace")
            except Exception:
                html = ham.decode("utf-8", errors="replace")

        metin = _html_temizle(html)
        return {"url": url, "metin": metin[:max_karakter], "toplam_karakter": len(metin)}
    except urllib.error.HTTPError as e:
        return {"url": url, "hata": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"url": url, "hata": str(e)}


def _html_temizle(html: str) -> str:
    """Basit HTML temizleyici — BeautifulSoup yoksa regex fallback."""
    try:
        from html.parser import HTMLParser

        class _Temizleyici(HTMLParser):
            def __init__(self):
                super().__init__()
                self._parcalar: list[str] = []
                self._atla = False

            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "head"):
                    self._atla = True

            def handle_endtag(self, tag):
                if tag in ("script", "style", "head"):
                    self._atla = False

            def handle_data(self, data):
                if not self._atla and data.strip():
                    self._parcalar.append(data.strip())

        t = _Temizleyici()
        t.feed(html)
        return " ".join(t._parcalar)
    except Exception:
        import re
        metin = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", metin).strip()


def ozet_al(url: str, provider=None) -> dict:
    """URL metnini LLM ile ozetle. Provider verilmezse ham metin doner."""
    icerik = url_oku(url, max_karakter=2000)
    if "hata" in icerik:
        return icerik
    metin = icerik["metin"]
    if not provider:
        return {"url": url, "ozet": metin[:500] + "..." if len(metin) > 500 else metin}
    try:
        prompt = f"Su metni 3 cumlede ozetle:\n\n{metin[:1500]}"
        ozet = provider.uret(prompt, [{"role": "user", "content": "Ozet yaz."}])
        return {"url": url, "ozet": ozet}
    except Exception as e:
        return {"url": url, "hata": str(e)}


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    komut = sys.argv[1] if len(sys.argv) > 1 else "ara"
    deger = sys.argv[2] if len(sys.argv) > 2 else "Python"

    if komut == "ara":
        sonuc = ara(deger)
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    elif komut == "url":
        sonuc = url_oku(deger)
        print(sonuc.get("metin", sonuc.get("hata", ""))[:1000])
    else:
        print(f"Kullanim: python {__file__} [ara|url] <deger>")
