# -*- coding: utf-8 -*-
"""dns_lookup.py — DNS sorgulama aracı.

Domain adreslerinin DNS kayıtlarını sorgular (A, AAAA, MX, NS, TXT).
"""

import json
import socket

# Opsiyonel: dnspython
try:
    import dns.resolver
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False


TOOL_META = {
    "aciklama": "Domain adreslerinin DNS kayıtlarını sorgular (A, AAAA, MX, NS, TXT).",
    "parametreler": [
        {"ad": "domain", "tip": "str", "aciklama": "Sorgulanacak domain adı (örn: google.com)."},
        {"ad": "kayit_tipi", "tip": "str", "aciklama": "DNS kayıt tipi: A, AAAA, MX, NS, TXT, CNAME (varsayılan: A)."},
    ],
    "ornek": 'DNS_LOOKUP("google.com", kayit_tipi="MX")',
    "kategori": "web",
}


def _socket_lookup(domain: str, kayit_tipi: str) -> dict:
    """Socket tabanlı basit DNS sorgulama."""
    if kayit_tipi == "A":
        try:
            addr = socket.gethostbyname(domain)
            return {"kayitlar": [addr], "kaynak": "socket"}
        except socket.gaierror as e:
            return {"hata": str(e), "kaynak": "socket"}
    elif kayit_tipi in ("AAAA", "MX", "NS", "TXT", "CNAME"):
        try:
            results = socket.getaddrinfo(domain, None)
            ipv6 = [r[4][0] for r in results if r[0] == socket.AF_INET6]
            if kayit_tipi == "AAAA" and ipv6:
                return {"kayitlar": ipv6, "kaynak": "socket"}
            elif kayit_tipi == "A" and not ipv6:
                ipv4 = [r[4][0] for r in results if r[0] == socket.AF_INET]
                return {"kayitlar": ipv4, "kaynak": "socket"}
            else:
                return {"kayitlar": ipv6 or [r[4][0] for r in results], "kaynak": "socket"}
        except socket.gaierror as e:
            return {"hata": f"Socket ile {kayit_tipi} sorgulanamadi: {str(e)}", "kaynak": "socket"}
    else:
        return {"hata": f"Socket ile {kayit_tipi} desteklenmiyor, dnspython kullanilmali.", "kaynak": "socket"}


def run(domain: str = "", kayit_tipi: str = "A", *args, **kwargs) -> str:
    """DNS sorgulaması yap.

    Args:
        domain: Sorgulanacak domain adı.
        kayit_tipi: DNS kayıt tipi (A, AAAA, MX, NS, TXT, CNAME).

    Returns:
        JSON: DNS kayıtları.
    """
    if not domain:
        return json.dumps({"hata": "domain parametresi zorunludur."}, ensure_ascii=False)

    kayit_tipi = kayit_tipi.upper()

    if HAS_DNSPYTHON:
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5

            if kayit_tipi == "A":
                answers = resolver.resolve(domain, "A")
                kayitlar = [str(r) for r in answers]
            elif kayit_tipi == "AAAA":
                answers = resolver.resolve(domain, "AAAA")
                kayitlar = [str(r) for r in answers]
            elif kayit_tipi == "MX":
                answers = resolver.resolve(domain, "MX")
                kayitlar = [f"{r.preference} {r.exchange}" for r in answers]
            elif kayit_tipi == "NS":
                answers = resolver.resolve(domain, "NS")
                kayitlar = [str(r) for r in answers]
            elif kayit_tipi == "TXT":
                answers = resolver.resolve(domain, "TXT")
                kayitlar = [" ".join(r.strings) for r in answers]
            elif kayit_tipi == "CNAME":
                answers = resolver.resolve(domain, "CNAME")
                kayitlar = [str(r) for r in answers]
            else:
                return json.dumps({"hata": f"Geçersiz kayıt tipi: {kayit_tipi}"}, ensure_ascii=False)

            return json.dumps({
                "domain": domain,
                "kayit_tipi": kayit_tipi,
                "kaynak": "dnspython",
                "kayit_sayisi": len(kayitlar),
                "kayitlar": kayitlar,
            }, ensure_ascii=False, indent=2)

        except dns.resolver.NoAnswer:
            return json.dumps({
                "domain": domain,
                "kayit_tipi": kayit_tipi,
                "durum": "kayit_bulunamadi",
                "kaynak": "dnspython",
            }, ensure_ascii=False, indent=2)
        except dns.resolver.NXDOMAIN:
            return json.dumps({
                "domain": domain,
                "kayit_tipi": kayit_tipi,
                "durum": "domain_bulunamadi",
                "kaynak": "dnspython",
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "domain": domain,
                "hata": str(e),
                "kaynak": "dnspython",
            }, ensure_ascii=False, indent=2)
    else:
        # Socket fallback
        sonuc = _socket_lookup(domain, kayit_tipi)
        sonuc["domain"] = domain
        sonuc["kayit_tipi"] = kayit_tipi
        sonuc["not"] = "dnspython kurulu degil, socket tabanli sinirli sorgu."
        return json.dumps(sonuc, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("=== DNS A (socket fallback) ===")
    print(run("google.com", kayit_tipi="A"))
    print("\n=== DNS MX ===")
    print(run("google.com", kayit_tipi="MX"))
