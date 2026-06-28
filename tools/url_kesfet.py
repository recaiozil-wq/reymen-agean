# -*- coding: utf-8 -*-
"""tools/url_kesfet.py — Bir URL'den tum baglantilari bul.

BeautifulSoup ile HTML parse eder, fallback olarak regex kullanir.
"""

import logging
import re
from urllib.parse import urljoin, urlparse
from typing import Optional

logger = logging.getLogger(__name__)

# Regex fallback — Sayfa icindeki href'leri yakalar
_HREF_REGEX = re.compile(
    r'''href=["'](.*?)["']''', re.IGNORECASE
)


def run(url: str = "", kaynak_metin: str = "", taban_url: str = "",
        filtre: str = "", **kwargs) -> dict:
    """Bir URL'den veya kaynak metinden tum baglantilari bul.

    Args:
        url: Indirilip parse edilecek URL (belirtilmezse kaynak_metin kullanilir)
        kaynak_metin: Dogrudan HTML metni (url bos ise kullanilir)
        taban_url: Goreceli baglantilari mutlak URL'ye cevirmek icin (zorunlu degil)
        filtre: Sadece belirtilen domain'i iceren baglantilari goster

    Returns:
        dict: {"basarili": bool, "cikti": [baglanti_listesi], "hata": str, "toplam": int}
    """
    try:
        html = ""
        kullanilan_taban = taban_url or url

        if url:
            # URL'den HTML indir
            html, hata = _html_indir(url)
            if hata:
                return {"basarili": False, "cikti": [], "hata": hata, "toplam": 0}
            kullanilan_taban = taban_url or url
        elif kaynak_metin:
            html = kaynak_metin
        else:
            return {
                "basarili": False, "cikti": [], "hata": "url veya kaynak_metin parametresi zorunludur.", "toplam": 0
            }

        baglantilar = _baglantilari_bul(html, kullanilan_taban)

        if filtre:
            baglantilar = [b for b in baglantilar if filtre.lower() in b.lower()]

        return {
            "basarili": True,
            "cikti": baglantilar,
            "hata": "",
            "toplam": len(baglantilar)
        }

    except Exception as e:
        logger.exception("URL kesfet hatasi")
        return {
            "basarili": False, "cikti": [], "hata": f"Beklenmeyen hata: {str(e)}", "toplam": 0
        }


def _html_indir(url: str) -> tuple:
    """Belirtilen URL'den HTML icerigi indir.

    Returns:
        (html_metin, hata_mesaji) — hata yoksa hata_mesaji = ""
    """
    try:
        import urllib.request
        import urllib.error
    except ImportError:
        return "", "urllib modulu bulunamadi."

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as yanit:
            charset = yanit.headers.get_content_charset() or "utf-8"
            html = yanit.read().decode(charset, errors="replace")
        return html, ""
    except urllib.error.HTTPError as e:
        return "", f"HTTP hatasi {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return "", f"URL hatasi: {e.reason}"
    except Exception as e:
        return "", f"Indirme hatasi: {str(e)}"


def _baglantilari_bul(html: str, taban_url: str = "") -> list:
    """HTML icindeki tum baglantilari BeautifulSoup ile bul,
    basarisiz olursa regex fallback kullan."""
    baglantilar = []

    # 1. Deneme: BeautifulSoup
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["a", "link", "area"]):
            href = tag.get("href") or ""
            href = href.strip()
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                if taban_url:
                    href = urljoin(taban_url, href)
                baglantilar.append(href)

        # iframe kaynaklari da ekle
        for tag in soup.find_all("iframe"):
            src = tag.get("src") or ""
            src = src.strip()
            if src:
                if taban_url:
                    src = urljoin(taban_url, src)
                baglantilar.append(src)

        if baglantilar:
            # Benzersiz yap
            return _benzersiz_koru_sirala(baglantilar)

    except ImportError:
        pass  # BeautifulSoup yok, regex fallback'e gec
    except Exception:
        logger.warning("BeautifulSoup parse hatasi, regex fallback kullaniliyor")

    # 2. Deneme: Regex fallback
    for eslesme in _HREF_REGEX.finditer(html):
        href = eslesme.group(1).strip()
        if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
            if taban_url:
                href = urljoin(taban_url, href)
            baglantilar.append(href)

    return _benzersiz_koru_sirala(baglantilar)


def _benzersiz_koru_sirala(baglantilar: list) -> list:
    """Baglantilari benzersiz yap ve sirala."""
    gorulen = set()
    sonuc = []
    for b in baglantilar:
        if b not in gorulen:
            gorulen.add(b)
            sonuc.append(b)
    return sorted(sonuc)


if __name__ == "__main__":
    print("=== URL KESFET ===")
    # Ornek: Yerel test
    test_html = """<html><body>
    <a href="/sayfa1">Sayfa 1</a>
    <a href="https://ornek.com/sayfa2">Sayfa 2</a>
    <a href="#bolum">Bolum</a>
    <a href="javascript:void(0)">JS</a>
    </body></html>"""
    print(run(kaynak_metin=test_html, taban_url="https://ornek.com"))
