
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Security_Guvenlik Izleme Sistemi_References_Windows Forensics Attack Perspective |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Windows Forensics — Saldirgan/Atak Perspektifi

## Bilgisayara El Konulursa Kesin Bulunacaklar (Silinemez)

| Iz | Konum | Ne Gosterir |
|----|-------|-------------|
| Windows Event Log | `C:\Windows\System32\winevt\Logs\` | Acilis saatleri, program calistirmalari, servis durumlari |
| USB takilis gecmisi | Registry `USBSTOR` | Hangi USB, seri no, takilma/sokulme zamanlari |
| Ag baglanti gecmisi | Registry `NLA` + `SRUM` | Hangi WiFi aglari, ne zaman |
| $MFT + USN Journal | NTFS metadata | Silinen dosya adlari, boyutlari, silinme zamanlari |
| VirtualBox kayitlari | Registry + XML | Kali VM kurulumu, MAC adresi, ag ayarlari |
| OneDrive senkronizasyon | OneDrive logs | Obsidian vault gecmisi (bulutta) |

## Az Bilinen Ama Kritik Izler

| Iz | Ne Kaydeder |
|----|-------------|
| $USN Journal | Her dosya islemi (silinen .md adlari bile durur) |
| Windows Timeline | "Saat 14:00'te Tor Browser acikti" |
| AmCache / ShimCache | Calistirilan her .exe'nin adi ve zamani |
| DNS Cache | Ziyaret edilen domain'ler |
| Volume Shadow Copy | Eski dosya versiyonlari |
| SRUM (System Resource Usage Monitor) | Process execution history, network usage |

## Korumali Olan / Olmayan (2026-06-11 itibariyle)

**Korumali:**
- Tor Browser profili (gecmis, cookie, onbellek, oturum) → startup'ta temizlenir
- Prefetch (firefox.exe) → startup'ta temizlenir
- Recent Items / Jump Lists → startup'ta temizlenir
- Pagefile (RAM takasi) → kapanista sifirlanir (ClearPageFileAtShutdown=1)

**Korumasiz / Kesin bulunur:**
- Event Log'lar (acilis saati, program calistirma)
- USBSTOR (Kali USB, flash bellekler)
- Kali VM kurulum kayitlari
- Obsidian vault (su an sifresiz, duz metin — VeraCrypt devam ediyor)
- OneDrive yedekleri (vault gecmisi bulutta)
- Telegram kullanimi
- Tor Browser'in kendisinin yuklu olmasi

## Korunma Sirasi

1. Obsidian vault sifreleme (VeraCrypt — devam ediyor)
2. Windows Timeline kapatma (GPO ile)
3. OneDrive baglantisini kesme / vault'u buluttan cikarma
4. Kali VM sifreleme (LUKS)
5. Event Log temizleme (loglari minimal tutma)
6. Shadow Copies temizleme
