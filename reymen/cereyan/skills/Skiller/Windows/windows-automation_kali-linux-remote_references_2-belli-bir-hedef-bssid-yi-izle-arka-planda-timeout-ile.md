
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_2 Belli Bir Hedef Bssid Yi Izle Arka Planda Timeout Ile |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# 2. Belli bir hedef BSSID'yi izle (arka planda, timeout ile)
ssh kali "sudo timeout 60 airodump-ng wlan0 --bssid <HEDEF_BSSID> --channel <CH> -w /tmp/airodump_out --output-format csv --write-interval 5 2>/dev/null"