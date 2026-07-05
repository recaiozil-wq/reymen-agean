"""
WiFi aÄŸÄ±ndaki cihazlarÄ± tara â€” IP + MAC adreslerini bul.

SelfHeal test Ã¶rneÄŸi:
1. nmap ile subnet tara
2. ARP tablosunu oku
3. SonuÃ§larÄ± tablo olarak gÃ¶ster
4. Hata olursa â†’ SelfHeal otomatik dÃ¼zeltir
"""

import subprocess, re, sys, json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# â”€â”€ 1. AÄŸ arayÃ¼zÃ¼nÃ¼ bul â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def aktif_interface_bul() -> str:
    """WiFi arayÃ¼zÃ¼nÃ¼n IP'sini bul â€” dynamic ARP entry'si olan tercih edilir."""
    try:
        # Ã–nce arp -a ile dynamic entry'si olan interface'i bul
        arp_r = subprocess.run(
            ["arp", "-a"], capture_output=True, text=False, timeout=15
        )
        arp_cikti = arp_r.stdout.decode("utf-8", errors="replace")

        # Her interface bloÄŸunu ayÄ±r
        bloklar = arp_cikti.split("Interface:")
        for blok in bloklar[1:]:  # ilk blok header
            ilk_satir = blok.splitlines()[0] if blok.splitlines() else ""
            m_if = re.search(r"(\d+\.\d+\.\d+\.\d+)", ilk_satir)
            if not m_if:
                continue
            if_ip = m_if.group(1)
            # Bu blokta dynamic entry var mÄ±?
            if "dynamic" in blok:
                return if_ip

        # Fallback: ipconfig
        r = subprocess.run(["ipconfig"], capture_output=True, text=False, timeout=15)
        cikti = r.stdout.decode("utf-8", errors="replace")
        for line in cikti.splitlines():
            m = re.search(r"IPv4[^:]*:\s*(\d+\.\d+\.\d+\.\d+)", line)
            if m:
                ip = m.group(1)
                if ip.startswith(("192.168.", "10.")):
                    return ip
    except Exception as e:
        print(f"[HATA] aktif_interface_bul: {e}")
    return ""


def subnet_bul(ip: str) -> str:
    """IP'den /24 subnet hesapla."""
    parts = ip.split(".")
    parts[-1] = "0"
    return ".".join(parts) + "/24"


# â”€â”€ 2. ARP tablosu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def arp_tara() -> list[dict]:
    """arp -a komutu ile cihazlarÄ± bul."""
    cihazlar = []
    try:
        r = subprocess.run(["arp", "-a"], capture_output=True, text=False, timeout=15)
        cikti = r.stdout.decode("utf-8", errors="replace")
        for line in cikti.splitlines():
            m = re.search(
                r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F\-]{17})\s+(dynamic|static)", line
            )
            if m:
                ip = m.group(1)
                mac = m.group(2).replace("-", ":").lower()
                tur = m.group(3)
                # Multicast/broadcast filtrele
                if not ip.startswith(("224.", "239.", "255.")):
                    cihazlar.append({"ip": ip, "mac": mac, "turu": tur})
    except Exception as e:
        print(f"[HATA] arp -a: {e}")
    return cihazlar


# â”€â”€ 3. Nmap taramasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def nmap_tara(subnet: str) -> list[dict]:
    """nmap -sn ile canlÄ± cihazlarÄ± tara."""
    cihazlar = []
    try:
        r = subprocess.run(
            ["nmap", "-sn", subnet], capture_output=True, text=False, timeout=60
        )
        cikti = r.stdout.decode("utf-8", errors="replace")
        ip_bulundu = None
        for line in cikti.splitlines():
            m_ip = re.search(r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)", line)
            if m_ip:
                ip_bulundu = m_ip.group(1)
                continue
            m_mac = re.search(r"MAC Address:\s+([0-9A-Fa-f:]{17})", line)
            if m_mac and ip_bulundu:
                mac = m_mac.group(1).lower()
                # Uretici bilgisi de var: MAC Address: XX:XX:XX:XX:XX:XX (Intel)
                uretici = ""
                u_m = re.search(r"MAC Address:\s+[0-9A-Fa-f:]{17}\s+\((.+)\)", line)
                if u_m:
                    uretici = u_m.group(1)
                if not ip_bulundu.startswith(("224.", "239.", "255.")):
                    cihazlar.append(
                        {
                            "ip": ip_bulundu,
                            "mac": mac,
                            "uretici": uretici,
                            "turu": "dynamic",
                        }
                    )
                ip_bulundu = None
    except subprocess.TimeoutExpired:
        print("[UYARI] nmap zaman aÅŸÄ±mÄ± (60s)")
    except FileNotFoundError:
        print("[UYARI] nmap bulunamadÄ±, sadece ARP kullanÄ±lacak")
    except Exception as e:
        print(f"[HATA] nmap: {e}")
    return cihazlar


# â”€â”€ 4. Ana â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def main():
    print("â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
    print("â•‘    WiFi Cihaz TaramasÄ± (IP + MAC)          â•‘")
    print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
    print()

    # AÄŸ bilgisi
    ip = aktif_interface_bul()
    if not ip:
        print("âŒ Aktif aÄŸ arayÃ¼zÃ¼ bulunamadÄ±.")
        return

    subnet = subnet_bul(ip)
    print(f"ğŸ“¡ ArayÃ¼z IP: {ip}")
    print(f"ğŸŒ Subnet:    {subnet}")
    print()

    # ARP tablosu
    print("ğŸ“‹ ARP tablosu taranÄ±yor...")
    arp_cihazlar = arp_tara()
    print(f"   ARP'de {len(arp_cihazlar)} cihaz bulundu")

    # Nmap taramasÄ±
    print("ğŸ” Nmap ile canlÄ± cihaz taranÄ±yor...")
    nmap_cihazlar = nmap_tara(subnet)
    print(f"   Nmap'te {len(nmap_cihazlar)} cihaz bulundu")

    # BirleÅŸtir (nmap Ã¶ncelikli)
    gorulen_ip = set()
    tum_cihazlar = []

    for c in nmap_cihazlar:
        gorulen_ip.add(c["ip"])
        tum_cihazlar.append(c)
    for c in arp_cihazlar:
        if c["ip"] not in gorulen_ip:
            gorulen_ip.add(c["ip"])
            tum_cihazlar.append(c)

    # SÄ±rala
    tum_cihazlar.sort(key=lambda x: [int(p) for p in x["ip"].split(".")])

    # Tablo gÃ¶ster
    print()
    print("â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”")
    print("â”‚ IP                  â”‚ MAC                â”‚ Ãœretici      â”‚")
    print("â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤")

    for c in tum_cihazlar:
        ip_str = c["ip"].ljust(19)
        mac_str = c["mac"].ljust(18)
        uretici = c.get("uretici", c.get("turu", ""))[:12].ljust(12)
        print(f"â”‚ {ip_str}â”‚ {mac_str}â”‚ {uretici}â”‚")

    print("â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜")
    print(f"\nğŸ“Š Toplam: {len(tum_cihazlar)} cihaz")

    # JSON Ã§Ä±ktÄ± (self_heal iÃ§in)
    cikti = {
        "zaman": datetime.now().isoformat(),
        "interface_ip": ip,
        "subnet": subnet,
        "cihaz_sayisi": len(tum_cihazlar),
        "cihazlar": tum_cihazlar,
    }
    with open("wifi_cihazlari_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(cikti, f, indent=2, ensure_ascii=False)
    print(f"\nğŸ’¾ JSON kaydedildi: wifi_cihazlari_sonuc.json")


if __name__ == "__main__":
    main()
