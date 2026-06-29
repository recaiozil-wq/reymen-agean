
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Vbox Klavye Iletimi_References_Ssh Den Alinan Sonuclari Echo Ile Vm Ekranina Yaz |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# SSH'den alinan sonuclari echo ile VM ekranina yaz
"VBoxManage.exe" controlvm "kal" keyboardputstring "echo 'TURKSAT-KABLONET-U0JG-2.4G'"
"VBoxManage.exe" controlvm "kal" keyboardputstring $'\n'
"VBoxManage.exe" controlvm "kal" keyboardputstring "echo '  Sinyal: -22 dBm'"
"VBoxManage.exe" controlvm "kal" keyboardputstring $'\n'
```

### Ralink RT2501/RT2573 Karakteristigi

| Ozelik | Deger |
|--------|-------|
| Chipset | rt2573 |
| Driver | rt73usb |
| Firmware | rt73.bin (v1.7) |
| Frekans | 2.4 GHz (sadece b/g) |
| Maks hiz | 54 Mbps |
| Kanal | 1-13 |

### Dikkat Edilecekler

1. **Bolge kodu kritik**: `iw reg set` yapilmazsa country=00 olur, tum kanallar PASSIVE-SCAN modunda calisir. Bu durumda arayuz sadece beacon duydugu aglari gorebilir — hicbir ag bulunamayabilir. Her zaman `iw reg set DE`/`TR` ile aktif taramayi etkinlestir.

2. **`iwlist` vs `iw scan`**: `iwlist` wireless extensions kullanir (Wi-Fi 7'de calismaz). `iw dev wlan0 scan -u` nl80211 ile daha guncel ve guvenilir. Ilki calismazsa ikinciyi dene.

3. **USB filtresi VM kapaliyken eklenmeli**: Running VM'e filtre eklenemez, once poweroff.

4. **xHCI controller**: VirtualBox varsayilan olarak OHCI/EHCI kullanir. USB 3.0 adaptorler icin `--usbxhci on` sart. Ralink gibi eski USB 2.0 adaptorlerde de bazen gerekebilir.

5. **VM reset sonrasi IP degisimi**: Kali bridged DHCP kullaniyorsa VM reset sonrasi yeni IP alabilir. MAC adresinden IP bul:
   ```bash
   arp -a | grep "08-00-27"
   ```

6. **`iw dev wlan0 scan` bos donerse**: Arayuz down olabilir (`ip link set wlan0 up`), power save acik olabilir (`set power_save off`), veya bolge kodu ayarlanmamis olabilir (`iw reg set DE`).

7. **`-u` flag'i kandirir**: `iw dev wlan0 scan -u` SADECE su anki kanali tarar. Telefon hotspot'i gibi baska kanaldaki aglari bulamazsin. Her zaman `-u` OLMADAN tara (`iw dev wlan0 scan`). Gercek tarama 5-15 saniye surer.

8. **Telefon hotspot'i AP olarak gorunur**: Telefonun WiFi erisim noktasi (hotspot) aciksa, Kali bunu normal bir AP gibi gorur — STA (istasyon) degil. SSID'si hotspot adi neyse o olarak listelenir. Sinyal seviyesi cok yuksekse (-12 dBm gibi) yaninda demektir.