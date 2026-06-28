
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Kt Bssid 46 89 9E Xx Xx Xx Signal 27 00 Dbm Freq 2437 Ssid S |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çıktı: BSSID 46:89:9e:xx:xx:xx, signal: -27.00 dBm, freq: 2437, SSID: S 22 PLAS
```

**Not:** WiFi adaptörü managed modda olsa bile `iw dev wlan0 scan` çalışır — monitor moda gerek yoktur.

#### Yöntem 2 — airodump-ng (Sadece Canlı Takip / Paket Yakalama İçin)

monitor mod gerektirir. **Doğrudan SSH üzerinden çalıştırma YASAK** — 1.6B karakter çıktı terminal tool'unu çökertebilir:

```
❌ bash: warning: command substitution: ignored null byte in input
❌ output parsing failed — Too large output (1609827929 bytes vs 90000 byte limit)
```

**Doğru yöntem — CSV çıktı + timeout + arka plan:**

```bash