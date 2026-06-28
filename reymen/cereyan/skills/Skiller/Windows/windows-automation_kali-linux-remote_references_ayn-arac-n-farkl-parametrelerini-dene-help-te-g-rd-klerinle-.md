
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Ayn Arac N Farkl Parametrelerini Dene Help Te G Rd Klerinle  |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Aynı aracın farklı parametrelerini dene (help'te gördüklerinle sınırlı kal)
```

**Kural:** Kullanıcı "help komutu ile yol bul" dediğinde, dış kaynaklardan (web, Tor) çözüm aramadan önce mutlaka önce Kali'de `--help`/`man` ile çözüm ara. Help'te yolu gösteren parametre varsa onu kullan, yoksa alternatif araçları help ile keşfet.

**Örnek akış (bu oturumda test edildi):**
```
iw → "device or resource busy" → iw --help ile wlan0 down/up/set type gör
    → managed moda geç → scan çalışır → S22 PLAS tespit edilir
    → monitor moda dön → airodump-ng ile canlı takip
```

Kali'ye USB Wi-Fi adaptörü takıldığında (RT2501/RT2573 / rt73usb) `wlan0` arayüzü **otomatik oluşmayabilir**. `lsusb` cihazı görür, `lsmod` sürücüyü gösterir ama `ip link show`'da wlan arayüzü yoktur. Bu durumda:

### Arayüzü Elle Oluştur

```bash