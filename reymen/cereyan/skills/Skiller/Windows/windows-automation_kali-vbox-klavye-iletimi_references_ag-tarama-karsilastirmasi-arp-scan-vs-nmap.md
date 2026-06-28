
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Vbox Klavye Iletimi_References_Ag Tarama Karsilastirmasi Arp Scan Vs Nmap |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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