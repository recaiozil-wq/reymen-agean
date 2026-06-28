---

name: kali-vbox-klavye-iletimi
description: VirtualBox VM icindeki Kali Linux terminaline klavye girisini VBoxManage keyboardputstring ile yapma + USB WiFi passthrough ve cevre ag taramasi.
title: "Kali Vbox Klavye Iletimi"

audience: user
tags: [automation, windows]
category: windows-automation---

# Kali Vbox Klavye Iletimi

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
| ÖNEMLİ — İlk Tercih Guest Control Olmalı | `references/nemli-i-lk-tercih-guest-control-olmal.md` |
| ZORUNLU ILK ADIM — Ekran Kontrolu | `references/zorunlu-ilk-adim-ekran-kontrolu.md` |
| Ne Zaman Kullanilir | `references/ne-zaman-kullanilir.md` |
| Prerequisites | `references/prerequisites.md` |
| Komutlar | `references/komutlar.md` |
| KULLANICI KURALLARI (DEGISTIRILEMEZ) | `references/kullanici-kurallari-degistirilemez.md` |
| Dikkat Edilecekler | `references/dikkat-edilecekler.md` |
| SSH + VBoxManage Birlikte Kullanim | `references/ssh-vboxmanage-birlikte-kullanim.md` |
| 1. SSH ile komutu calistir, ciktiyi al | `references/1-ssh-ile-komutu-calistir-ciktiyi-al.md` |
| 2. Ozeti VM terminaline yazdir | `references/2-ozeti-vm-terminaline-yazdir.md` |
| Ag Tarama Karsilastirmasi (arp-scan vs nmap) | `references/ag-tarama-karsilastirmasi-arp-scan-vs-nmap.md` |
| Ornek: VirtualBox'a dogrudan komut yazip calistirma | `references/ornek-virtualbox-a-dogrudan-komut-yazip-calistirma.md` |
| Adim 1: Giris mesaji | `references/adim-1-giris-mesaji.md` |
| Adim 2: Ag tarama | `references/adim-2-ag-tarama.md` |
| Adim 3: Detayli tarama | `references/adim-3-detayli-tarama.md` |
| USB WiFi Passthrough (Ralink RT2501/RT2573 + benzeri) | `references/usb-wifi-passthrough-ralink-rt2501-rt2573-benzeri.md` |
| 2. USB filtresi ekle (VM KAPALIYKEN) | `references/2-usb-filtresi-ekle-vm-kapaliyken.md` |
| 3. xHCI (USB 3.0) kontrolcuyu etkinlestir | `references/3-xhci-usb-3-0-kontrolcuyu-etkinlestir.md` |
| 4. VM'i baslat | `references/4-vm-i-baslat.md` |
| rt73usb driver + rt73.bin firmware (v1.7) | `references/rt73usb-driver-rt73-bin-firmware-v1-7.md` |
| Arayuzu aktif et | `references/arayuzu-aktif-et.md` |
| Power save kapat (arama icin onemli) | `references/power-save-kapat-arama-icin-onemli.md` |
| veya: sudo iw reg set TR | `references/veya-sudo-iw-reg-set-tr.md` |
| veya eski API: | `references/veya-eski-api.md` |
| SSH'den alinan sonuclari echo ile VM ekranina yaz | `references/ssh-den-alinan-sonuclari-echo-ile-vm-ekranina-yaz.md` |
| Problem Giderme | `references/problem-giderme.md` |
| Referans Dosyalari | `references/referans-dosyalari.md` |

## Kullanım

1. İhtiyacın olan bölümü belirle
2. `skill_view(name="...", file_path="references/...")` ile yükle
