"""
Web site politikası aracı.
robots.txt okuma, rate limit, izin listesi.
"""
import re
import time
from urllib.parse import urlparse

_IZIN_LISTESI = set()
_RATE_LIMIT_KAYITLARI = {}


def _robots_tara(url):
    """robots.txt oku ve parse et."""
    try:
        from urllib.request import urlopen
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            response = urlopen(robots_url, timeout=5)
            icerik = response.read().decode('utf-8', errors='replace')
            return icerik, None
        except Exception as e:
            return None, f"robots.txt okunamadı: {str(e)}"
    except ImportError:
        return None, "requests/urllib modülü gerekli."


def run(islem='kontrol', url=None, **kwargs):
    """
    Web site politikası.

    Parametreler:
        islem (str): 'kontrol', 'robot_tara' veya 'izin_verilen'
        url (str): Web sitesi URL'si

    Returns:
        str: İşlem sonucu.
    """
    global _IZIN_LISTESI, _RATE_LIMIT_KAYITLARI

    try:
        if islem == 'robot_tara':
            if not url:
                return "Hata: 'url' parametresi zorunludur."
            icerik, hata = _robots_tara(url)
            if hata:
                return hata
            if icerik:
                return f"robots.txt ({url}):\n{icerik[:3000]}" + ("\n...(devamı)" if len(icerik) > 3000 else "")
            return f"{url} için robots.txt bulunamadı."

        elif islem == 'kontrol':
            if not url:
                return "Hata: 'url' parametresi zorunludur."

            # robots.txt kontrolü
            icerik, hata = _robots_tara(url)
            sonuc = []

            if hata:
                sonuc.append(f"robots.txt: {hata}")
                sonuc.append("Durum: İZİN VERİLDİ (robots.txt okunamadı)")

            elif icerik:
                parsed = urlparse(url)
                path = parsed.path or '/'
                disallowed = re.findall(r'Disallow:\s*(.*)', icerik, re.IGNORECASE)
                engelli = False
                for d in disallowed:
                    d = d.strip()
                    if d and path.startswith(d):
                        engelli = True
                        break
                if engelli:
                    sonuc.append(f"robots.txt: {url} engellenmiş olabilir (Disallow: {d})")
                    sonuc.append("Durum: ENGELLENMİŞ OLABİLİR")
                else:
                    sonuc.append("robots.txt: İzin veriliyor")
                    sonuc.append("Durum: İZİN VERİLDİ")
            else:
                sonuc.append("robots.txt: Bulunamadı")
                sonuc.append("Durum: İZİN VERİLDİ")

            return "\n".join(sonuc)

        elif islem == 'izin_verilen':
            if not _IZIN_LISTESI:
                return "İzin verilen site bulunamadı."
            liste = "\n".join([f"  - {s}" for s in sorted(_IZIN_LISTESI)])
            return f"İzin verilen siteler ({len(_IZIN_LISTESI)}):\n{liste}"

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'kontrol', 'robot_tara' veya 'izin_verilen' kullanın."

    except Exception as e:
        return f"Web site politikası hatası: {str(e)}"


def check_website_access(url: str) -> bool:
    """URL'nin erişime kapalı (engellenmiş) olup olmadığını kontrol et.

    Firecrawl ve benzeri web araçlarının politika kapısı olarak kullandığı
    fonksiyon. robots.txt ve dahili kara listeye göre değerlendirir.

    Args:
        url: Kontrol edilecek tam URL.

    Returns:
        bool: True → erişim ENGELLENDI, False → erişime izin verildi.
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        # Dahili kara liste
        ENGELLI_DOMAINLER = {
            "localhost", "127.0.0.1", "0.0.0.0", "::1",
            "169.254.169.254",  # AWS metadata
        }
        if netloc in ENGELLI_DOMAINLER or netloc.endswith(".local"):
            return True

        # robots.txt kontrolü
        icerik, hata = _robots_tara(url)
        if hata or not icerik:
            return False  # erişilemeyen robots.txt → izin ver

        path = parsed.path or "/"
        disallowed = re.findall(r'Disallow:\s*(.*)', icerik, re.IGNORECASE)
        for d in disallowed:
            d = d.strip()
            if d and path.startswith(d):
                return True  # engellendi

        return False  # izin verildi
    except Exception:
        return False  # hata durumunda izin ver
