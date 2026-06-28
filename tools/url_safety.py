# -*- coding: utf-8 -*-
"""tools/url_safety.py — URL guvenlik sarmalayicisi.

Kok dizindeki url_safety.py modulunu import eder ve
url_guvenli_mi() ile url_temizle() fonksiyonlarini delegasyonla calistirir.
"""


def run(islem='kontrol', **kwargs) -> str:
    """URL guvenlik islemlerini yonetir.

    Parametreler:
        islem (str): 'kontrol' veya 'temizle'
        url (str): Kontrol edilecek/temizlenecek URL

    Returns:
        str: Islem sonucu.
    """
    try:
        from url_safety import url_guvenli_mi, url_temizle

        url = kwargs.get('url', '')
        if not url:
            return "Hata: 'url' parametresi zorunludur."

        if islem == 'kontrol':
            guvenli, mesaj = url_guvenli_mi(url)
            durum = "GUVENLI" if guvenli else "ENGELLENDI"
            if mesaj:
                return f"[{durum}] {url} -> {mesaj}"
            return f"[{durum}] {url}"

        elif islem == 'temizle':
            temiz_url = url_temizle(url)
            return f"Temizlenmis URL: {temiz_url}"

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"URL guvenlik hatasi: {e}"


def is_safe_url(url: str) -> bool:
    """URL'nin güvenli olup olmadığını kontrol et (SSRF koruması).

    Args:
        url: Kontrol edilecek URL.

    Returns:
        bool: True → güvenli, False → engellendi/şüpheli.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https"):
            return False
        netloc = parsed.hostname or ""
        ENGELLI = {"localhost", "127.0.0.1", "0.0.0.0", "::1",
                   "169.254.169.254", "metadata.google.internal"}
        if netloc in ENGELLI:
            return False
        if netloc.endswith(".local") or netloc.endswith(".internal"):
            return False
        import ipaddress
        try:
            ip = ipaddress.ip_address(netloc)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            pass
        return True
    except Exception:
        return False
