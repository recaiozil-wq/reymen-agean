---
skill_id: 8a20e2b0822c
usage_count: 1
last_used: 2026-06-16
---
## Samsung / One UI 8 / Android 16 Sideload Sorun Giderme

**Belirti**: APK yüklenmeye çalışırken Google Play Protect "engellendi" diyor,
"Anladım" butonuna basınca "Uygulama yüklenmedi" hatası alınıyor.

**Sebep**: 2026 itibarıyla Google + Samsung çift katman güvenlik:
1. **Google Play Protect** — bilinmeyen geliştirici imzasını engeller
2. **Samsung Auto Blocker** (One UI 8) — Knox tabanlı ek güvenlik
3. **Android 16** — yeni kurulum kısıtlamaları, hedef SDK kontrolü
4. **Android 16 Stalkerware Detection** — FOREGROUND_SERVICE + RECORD_AUDIO kombinasyonu yükleme zamanında tespit edilip engellenir (Play Protect ve Auto Blocker'dan bağımsız). Detay: `references/android16-stalkerware-detection.md`

**Çözüm sırası (en kolaydan en zora):**

### A. Play Protect + Samsung Ayarları
```
1. Ayarlar > Güvenlik ve gizlilik > Otomatik Engelleyici → KAPAT
2. Ayarlar > Biyometri ve güvenlik > Bilinmeyen uygulamalar > Telegram → İzin ver
3. Telefonu kapat/aç (RAM'daki Play Protect önbelleği silinsin)
```

### B. ADB ile Bilgisayardan Yükle (KESİN ÇÖZÜM)
Bu yöntem **Play Protect ve Knox'u bypass eder**, direkt sisteme yazar.

```bash