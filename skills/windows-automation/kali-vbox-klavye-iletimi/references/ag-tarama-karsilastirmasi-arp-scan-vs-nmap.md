---
skill_id: 090e2527c6d1
usage_count: 1
last_used: 2026-06-16
---
## Ag Tarama Karsilastirmasi (arp-scan vs nmap)

| Ozelik | arp-scan | nmap -sn |
|--------|----------|----------|
| Sure | ~1.8 sn | ~3.5 sn |
| Cihaz sayisi | 7 (daha fazla) | 6 |
| Vendor bilgisi | Yok | Var |
| Protokol | ARP (L2) | ICMP+TCP (L3) |
| Kendini listeler | Hayir | Evet |

**Tavsiye**: Once `arp-scan` ile hizli on tarama, sonra `nmap -sn` ile vendor detayi.