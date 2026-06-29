
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_5 Temizlik |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# 5. Temizlik
ssh kali "sudo pkill airodump-ng; sudo iw dev wlan0 set type managed; sudo ip link set wlan0 up"
```

#### Hızlı Karar Akışı

```
Taramaya mı başlayacaksın?
├── SSID/AP tespiti yeterli mi?
│   ├── EVET → iw dev wlan0 scan (managed mod, hızlı)
│   └── HAYIR (canlı takip/paket yakalama) → airodump-ng (monitor mod)
│
├── Şu an hangi modda?
│   ├── managed → direkt iw dev wlan0 scan
│   └── monitor → önce managed moda geç, sonra iw dev wlan0 scan
│
└── Sinyal takibi mi yapacaksın?
    └── EVET → managed modda iw veya airodump-ng (monitor)
```

**Pitfall:** S22 PLAS gibi Samsung hotspot'lar **rastgele MAC** kullanır — her taramada BSSID değişebilir. SSID'den takip et (`grep -i "S22 PLAS"`). Sinyal seviyesi -27 dBm civarındaysa cihaz ~1-3 metre mesafededir.

#### managed ↔ monitor Geçişi

```bash