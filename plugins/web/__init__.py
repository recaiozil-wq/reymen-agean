# -*- coding: utf-8 -*-
"""plugins/web/__init__.py — Web Arama Plugin Kayit Defteri.

Birden cok web kaynagindan arama (brave, tavily, ddgs).
Alt pluginleri import eder ve motor_kaydet() uzerinden kaydeder.
"""


__all__ = ['motor_kaydet', 'web_ara', 'web_getir']
import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "web"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Birden cok web kaynagindan arama ve icerik getirme"

_web_plugins = []

try:
    from plugins.web import brave as _brave
    _web_plugins.append(_brave)
except ImportError:
    logger.debug("brave web plugin yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.web import tavily as _tavily
    _web_plugins.append(_tavily)
except ImportError:
    logger.debug("tavily web plugin yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")


def motor_kaydet(motor):
    """Tum web alt pluginlerini motor'a kaydeder.

    Ayrica temel web arama ve getirme araclarini da ekler.

    Args:
        motor: Motor ornegi
    """
    # Alt pluginleri kaydet
    for wp in _web_plugins:
        try:
            if hasattr(wp, "motor_kaydet"):
                wp.motor_kaydet(motor)
        except Exception as e:
            logger.warning("Web alt plugin kayit hatasi: %s", e)

    # Temel web araclari (bagimsiz - ek kutuphane gerektirmez)
    try:
        import json
        import urllib.request
        import urllib.parse

        def web_ara(args):
            """Web'de arama yap (DuckDuckGo HTML tabanli)."""
            sorgu = args.strip() if isinstance(args, str) else args.get("sorgu", "")
            if not sorgu:
                return "[Web] Arama sorgusu gerekli."
            try:
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(sorgu)}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                import re
                sonuclar = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^\"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
                if sonuclar:
                    satirlar = [f"{i+1}. {baslik.strip()}: {link}" for i, (link, baslik) in enumerate(sonuclar[:5])]
                    return "[Web] Sonuclar:\n" + "\n".join(satirlar)
                return f"[Web] '{sorgu}' icin sonuc bulunamadi."
            except Exception as e:
                return f"[Web] Arama hatasi: {e}"

        def web_getir(args):
            """Belirtilen URL'deki icerigi getir."""
            url = args.strip() if isinstance(args, str) else args.get("url", "")
            if not url:
                return "[Web] URL gerekli."
            if not url.startswith("http"):
                url = "https://" + url
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    icerik = resp.read().decode("utf-8", errors="replace")
                import re
                metin = re.sub(r"<[^>]+>", " ", icerik)
                metin = re.sub(r"\s+", " ", metin).strip()
                return metin[:2000] + ("..." if len(metin) > 2000 else "")
            except Exception as e:
                return f"[Web] Getirme hatasi: {e}"

        if hasattr(motor, "_plugin_arac_kaydet"):
            motor._plugin_arac_kaydet("WEB_ARA", web_ara, "Web'de arama yapar")
            motor._plugin_arac_kaydet("WEB_GETIR", web_getir, "URL icerigini getirir")
        elif hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("WEB_ARA", web_ara)
            motor._registry.kaydet("WEB_GETIR", web_getir)
    except Exception:
        logger.warning("[Plugin:web] Temel web araclari yuklenemedi.")

    logger.info("[Plugin:web] %d web alt plugin kayit edildi.", len(_web_plugins))
