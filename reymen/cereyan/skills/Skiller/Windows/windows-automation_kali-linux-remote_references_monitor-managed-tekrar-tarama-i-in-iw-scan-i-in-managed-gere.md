
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Monitor Managed Tekrar Tarama I In Iw Scan I In Managed Gere |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# monitor → managed (tekrar tarama için — iw scan için managed gerekir)
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up
sleep 1
```

#### airodump-ng Büyük Çıktı Yönetimi (SSH Üzerinden) — Yedek Referans

`airodump-ng` her saniye tüm istasyon listesini yeniden yazar. SSH üzerinden doğrudan çalıştırıldığında **devasa çıktı (1.6B+ karakter)** üretebilir:

**DOĞRU — CSV çıktı + timeout + write-interval:**
```bash
ssh kali "sudo timeout 60 airodump-ng wlan0 -w /tmp/scan --output-format csv --write-interval 5 2>/dev/null; cat /tmp/scan-01.csv 2>/dev/null"
```
- `--output-format csv`: Yapılandırılmış çıktı (BSSID'ler + istasyonlar ayrı)
- `--write-interval 5`: 5 sn'de bir yaz (çıktı boyutunu 1/5'e düşürür)
- `timeout 60`: 60 sn sonra otomatik durdur

**CSV'den istasyonları filtreleme:**
```bash
cat /tmp/scan-01.csv | awk -F, 'NR>2 && $1 ~ /^[A-Fa-f0-9:]{17}$/ {print $1, $6}'
```

**YANLIŞ — doğrudan airodump-ng** (terminal çöker):
```bash
ssh kali "sudo airodump-ng wlan0 2>/dev/null"  # YAPMA
```

#### Help-First Metodolojisi (Kullanıcı Tercihi)

Kullanıcı, her yeni araç/komut için **önce help menüsünü okuma, sonra uygulama** yaklaşımını tercih ediyor. Doğrudan çözüm üretmek yerine aracın kendi dokümantasyonundan yol bulmak:

```bash