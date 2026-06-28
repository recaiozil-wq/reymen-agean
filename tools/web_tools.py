#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_tools.py — Web araçları.
URL doğrulama, HTML çekme, içerik temizleme.
"""

import json
import re
import urllib.parse
import urllib.request
import urllib.error


def _url_dogrula(url):
    """URL'in geçerli olup olmadığını kontrol et."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme and parsed.netloc:
            return {
                "gecerli": True,
                "sema": parsed.scheme,
                "domain": parsed.netloc,
                "yol": parsed.path,
                "sorgu": parsed.query
            }
        return {"gecerli": False, "mesaj": "Eksik URL yapısı (scheme veya netloc)"}
    except Exception as e:
        return {"gecerli": False, "mesaj": str(e)}


def _html_getir(url, timeout=15):
    """URL'den HTML içerik çek."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as yanit:
            icerik = yanit.read().decode('utf-8', errors='replace')
            return {
                "durum": "basarili",
                "kod": yanit.getcode(),
                "boyut": len(icerik),
                "icerik": icerik,
                "headers": dict(yanit.headers)
            }
    except urllib.error.HTTPError as e:
        return {"durum": "hata", "kod": e.code, "mesaj": str(e)}
    except urllib.error.URLError as e:
        return {"durum": "hata", "mesaj": f"URL hatası: {e.reason}"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _icerik_temizle(html):
    """HTML içeriğini temizle (etiketleri kaldır, düz metin yap)."""
    if not html:
        return ""
    
    # Script ve style etiketlerini kaldır
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # HTML etiketlerini kaldır
    html = re.sub(r'<[^>]+>', ' ', html)
    
    # HTML entity'leri decode et
    html = html.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    html = html.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    
    # Boşlukları düzenle
    html = re.sub(r'\s+', ' ', html).strip()
    
    # Çoklu satır boşluklarını temizle
    html = re.sub(r'\n\s*\n', '\n', html)
    
    return html


def run(islem="dogrula", url=""):
    """
    Web araçları.
    
    Parametreler:
        islem (str): getir / dogrula / temizle
        url (str): URL adresi (getir/dogrula) veya HTML içerik (temizle)
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "dogrula":
            if not url:
                return json.dumps({"durum": "hata", "mesaj": "url parametresi gerekli"}, ensure_ascii=False)
            sonuc = _url_dogrula(url)
            return json.dumps({
                "durum": "basarili" if sonuc["gecerli"] else "hata",
                "url": url,
                "dogrulama": sonuc
            }, ensure_ascii=False)

        elif islem == "getir":
            if not url:
                return json.dumps({"durum": "hata", "mesaj": "url parametresi gerekli"}, ensure_ascii=False)
            sonuc = _html_getir(url)
            if sonuc["durum"] == "basarili":
                # İçeriği kısalt (çok büyükse)
                icerik = sonuc["icerik"]
                if len(icerik) > 50000:
                    sonuc["icerik"] = icerik[:50000] + f"\n... [toplam {len(icerik)} karakter, ilk 50000 gösteriliyor]"
                sonuc["icerik_temiz"] = _icerik_temizle(icerik)[:10000]
            return json.dumps(sonuc, ensure_ascii=False, default=str)

        elif islem == "temizle":
            if not url:
                return json.dumps({"durum": "hata", "mesaj": "url (HTML içerik) parametresi gerekli"}, ensure_ascii=False)
            temiz = _icerik_temizle(url)
            return json.dumps({
                "durum": "basarili",
                "orijinal_boyut": len(url),
                "temiz_boyut": len(temiz),
                "icerik": temiz[:10000],
                "mesaj": f"{len(url)} -> {len(temiz)} karakter (ilk 10000 gösteriliyor)"
            }, ensure_ascii=False)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("dogrula", "https://example.com"))
    print(run("temizle", "<html><body><h1>Merhaba</h1><p>Dünya</p></body></html>"))
