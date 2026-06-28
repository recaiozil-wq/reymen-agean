---
skill_id: 8ec51adcd0eb
usage_count: 1
last_used: 2026-06-16
---
# ADB'den emülatörü görünce APK'yı yükle
```

**Gradle Sync bekleme:**
- `"Importing '...' Gradle Project"` alt status bar'da görünür
- `"Gradle Build Running"` status bar'da görünür
- Sync tamamlanana kadar Run butonu pasiftir (gri)
- Sync bittiğinde emülatör otomatik bağlanır (`localhost:XXXXX device` ADB'de)

**Klavye kısayolu ile çalıştırma (tercih edilen):**
1. Pencereye tıkla/aktif et
2. `Shift+F10` = Run / Çalıştır
3. İzin dialog'larından geç (mikrofon, depolama vb.)

#### Emülatör / AVD:
- Eğer AVD yoksa: `sdkmanager.bat "system-images;android-35;google_apis;x86_64"` (büyük dosya, ~1.5GB, indirme sırasında timeout olabilir → `--no_https` veya arka planda çalıştır)
- Veya Android Studio içinden "Device Manager" ile oluştur
- Mevcut emülatörü CLI'den başlat: `emulator.exe -avd <avd_adi>`
- **Pitfall:** `avdmanager create avd` SDK XML v4 uyarısı + "Package path is not valid" hatası verebilir. Çözüm: sdkmanager ile indirildikten sonra bile `.installer` dosyası kalmışsa sil ve yeniden indir, veya Android Studio'dan AVD oluştur.

#### Emülatör Bağlantısı Kesildi/Kayboldu:
Emülatör process'i kapandıysa (tasklist'te yok, `adb devices` boş):
1. AVD var mı kontrol et: `ls ~/.android/avd/`
2. Yoksa → Android Studio'dan veya `avdmanager` ile yeniden oluştur
3. `emulator.exe -avd <adi>` ile başlat
4. ADB'den görünene kadar bekle
5. Sonra `adb install` ve test devam

### C. Fiziksel Cihaz

```bash