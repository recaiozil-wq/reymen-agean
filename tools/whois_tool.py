# -*- coding: utf-8 -*-
"""whois_tool.py — WHOIS sorgulama aracı.

Domain adreslerinin WHOIS bilgilerini sorgular.
python-whois yoksa socket ile basit sorgu dener.
"""

import json
import socket

# Opsiyonel: python-whois
try:
    import whois
    HAS_WHOIS = True
except ImportError:
    HAS_WHOIS = False


# WHOIS sunucuları (socket tabanlı sorgu için)
WHOIS_SUNUCULARI = {
    "com": "whois.verisign-grs.com",
    "net": "whois.verisign-grs.com",
    "org": "whois.pir.org",
    "io": "whois.nic.io",
    "gov": "whois.dotgov.gov",
    "edu": "whois.educause.edu",
    "info": "whois.afilias.net",
    "biz": "whois.biz",
    "me": "whois.nic.me",
    "dev": "whois.nic.google",
    "app": "whois.nic.google",
    "xyz": "whois.nic.xyz",
    "tr": "whois.nic.tr",
}


TOOL_META = {
    "aciklama": "Domain adreslerinin WHOIS bilgilerini sorgular.",
    "parametreler": [
        {"ad": "domain", "tip": "str", "aciklama": "Sorgulanacak domain adı (örn: google.com)."},
    ],
    "ornek": 'WHOIS_TOOL("ornek.com")',
    "kategori": "web",
}


def _socket_whois(domain: str) -> dict:
    """Socket ile basit WHOIS sorgulama."""
    try:
        uzanti = domain.split(".")[-1].lower()
        sunucu = WHOIS_SUNUCULARI.get(uzanti, f"whois.nic.{uzanti}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((sunucu, 43))
        sock.send(f"{domain}\r\n".encode("utf-8"))

        yanit = b""
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                yanit += data
            except socket.timeout:
                break
        sock.close()

        metin = yanit.decode("utf-8", errors="replace")[:10000]

        # Temel bilgileri ayıkla
        sonuc = {"domain": domain, "whois_sunucu": sunucu, "ham_yanit": metin}

        # Basit ayrıştırma
        for satir in metin.split("\n"):
            satir = satir.strip()
            if ":" in satir:
                anahtar, deger = satir.split(":", 1)
                anahtar = anahtar.strip().lower()
                deger = deger.strip()

                if anahtar in ("domain name", "domain"):
                    sonuc["domain_ad"] = deger
                elif anahtar in ("registrar", "registrar name"):
                    sonuc["kayit_sirketi"] = deger
                elif anahtar in ("creation date", "created"):
                    sonuc["olusturma_tarihi"] = deger
                elif anahtar in ("expiration date", "expiry date", "expire"):
                    sonuc["son_kullanim_tarihi"] = deger
                elif anahtar in ("name server", "nserver"):
                    if "name_server" not in sonuc:
                        sonuc["name_server"] = []
                    sonuc["name_server"].append(deger)
                elif anahtar in ("status", "domain status"):
                    if "durum" not in sonuc:
                        sonuc["durum"] = []
                    sonuc["durum"].append(deger)

        return sonuc

    except Exception as e:
        return {"domain": domain, "hata": str(e), "kaynak": "socket"}


def run(domain: str = "", *args, **kwargs) -> str:
    """WHOIS sorgulaması yap.

    Args:
        domain: Sorgulanacak domain adı.

    Returns:
        JSON: WHOIS bilgileri.
    """
    if not domain:
        return json.dumps({"hata": "domain parametresi zorunludur."}, ensure_ascii=False)

    if HAS_WHOIS:
        try:
            w = whois.whois(domain)
            sonuc = {
                "domain": domain,
                "kaynak": "python-whois",
                "domain_ad": w.domain_name or [],
                "kayit_sirketi": w.registrar or "",
                "whois_sunucu": w.whois_server or "",
                "olusturma_tarihi": str(w.creation_date) if w.creation_date else "",
                "son_kullanim_tarihi": str(w.expiration_date) if w.expiration_date else "",
                "guncelleme_tarihi": str(w.updated_date) if w.updated_date else "",
                "name_server": w.name_servers or [],
                "durum": w.status or [],
                "email": w.emails or [],
                "ulke": w.country or "",
            }
            return json.dumps(sonuc, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "domain": domain,
                "hata": f"python-whois hatasi: {str(e)}",
                "kaynak": "python-whois",
                "not": "Socket fallback deneniyor..."
            }, ensure_ascii=False, indent=2)

    # Socket fallback
    sonuc = _socket_whois(domain)
    sonuc["not"] = "python-whois kurulu degil, socket tabanli sinirli sorgu."
    return json.dumps(sonuc, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("=== WHOIS ===")
    print(run("google.com"))
