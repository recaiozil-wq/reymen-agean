# -*- coding: utf-8 -*-
"""ip_info.py — IP adresi bilgi sorgulama aracı.

IP adresinin detaylarını gösterir: versiyon, sınıf, özel mi, loopback mi.
Opsiyonel olarak harici IP'yi de öğrenir.
"""

import json
import socket
import ipaddress


TOOL_META = {
    "aciklama": "IP adresi bilgilerini gösterir: versiyon, sınıf, özel/loopback kontrolü.",
    "parametreler": [
        {"ad": "ip_adresi", "tip": "str", "aciklama": "Sorgulanacak IP adresi (boş = harici IP'mi öğren)."},
    ],
    "ornek": 'IP_INFO("192.168.1.1")',
    "kategori": "web",
}


def _harici_ip_ogren() -> str:
    """Harici IP adresini öğren."""
    try:
        import urllib.request
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        try:
            with urllib.request.urlopen("https://checkip.amazonaws.com", timeout=5) as resp:
                return resp.read().decode("utf-8").strip()
        except Exception:
            return None


def run(ip_adresi: str = "", *args, **kwargs) -> str:
    """IP adresi bilgisini sorgula.

    Args:
        ip_adresi: Sorgulanacak IP adresi (boş = harici IP'yi öğren).

    Returns:
        JSON: IP bilgileri.
    """
    try:
        # IP belirtilmemişse harici IP'yi öğren
        dis_ip = None
        if not ip_adresi:
            dis_ip = _harici_ip_ogren()
            if not dis_ip:
                return json.dumps({"hata": "IP adresi belirtilmedi ve harici IP ogrenilemedi."}, ensure_ascii=False)
            ip_str = dis_ip
        else:
            ip_str = ip_adresi.strip()

        # IP adresini parse et
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError as e:
            return json.dumps({"hata": f"Gecersiz IP adresi: {str(e)}"}, ensure_ascii=False)

        bilgi = {
            "ip": str(ip),
            "versiyon": f"IPv{ip.version}",
            "ozel": ip.is_private,
            "loopback": ip.is_loopback,
            "link_local": ip.is_link_local,
            "multicast": ip.is_multicast,
            "global": ip.is_global if ip.version == 4 else ip.is_global,
            "reserved": ip.is_reserved,
            "unspecified": ip.is_unspecified,
        }

        # IPv4 için sınıf bilgisi
        if ip.version == 4:
            octet1 = int(str(ip).split(".")[0])
            if octet1 < 128:
                bilgi["sinif"] = "A"
            elif octet1 < 192:
                bilgi["sinif"] = "B"
            elif octet1 < 224:
                bilgi["sinif"] = "C"
            elif octet1 < 240:
                bilgi["sinif"] = "D"
            else:
                bilgi["sinif"] = "E"

        # Ters DNS sorgulaması
        try:
            hostname, _, _ = socket.gethostbyaddr(str(ip))
            bilgi["hostname"] = hostname
        except (socket.herror, socket.gaierror):
            bilgi["hostname"] = "cozulemedi"

        if dis_ip:
            bilgi["not"] = "Bu sizin harici IP adresiniz."

        return json.dumps(bilgi, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== IP BILGISI ===")
    print(run("192.168.1.1"))
    print("\n=== HARICI IP ===")
    print(run())
