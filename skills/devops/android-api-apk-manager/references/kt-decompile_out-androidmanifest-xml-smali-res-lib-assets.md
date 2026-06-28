---
skill_id: f8aa95e26bb4
usage_count: 1
last_used: 2026-06-16
---
# Çıktı: decompile_out/AndroidManifest.xml, smali/, res/, lib/, assets/
```

#### 4. Değişiklikleri Yap

**Manifest düzenleme:**
- `targetSdkVersion` → 35 (Android 15, en güvenilir)
- `minSdkVersion` → cihaz SDK'sından düşük olmalı
- Split APK referanslarını temizle: `android:isSplitRequired="false"` veya sil, `split` niteliğini kaldır
- Foreground service ekle: `<service android:name=".KeepAliveService" android:exported="false" android:foregroundServiceType="microphone" />`

**Smali ekleme:**
- Yeni bir `.smali` dosyası oluştur (KeepAliveService, BroadcastReceiver vb.)
- Referans için `references/apk-smali-service-template.md` kullan

**Native lib'leri düzeltme:**
- apktool build bazen native lib'leri sıkıştırır (`compress_type=8`) ama `extractNativeLibs="false"` kalırsa Android açamaz
- Çözüm: `extractNativeLibs="true"` yap VEYA APK'yı build sonrası uncompressed lib'lerle yeniden paketle
- Düzeltme: `apktool b` sonrası çıkan APK'yı zip aç, `lib/` klasörünü uncompressed olarak yeniden ekle

#### 5. Rebuild Et
```bash
java -jar apktool.jar b decompile_out/ -o rebuilt_unsigned.apk
```

#### 6. İmzala

**Android 16 için ZORUNLU: V2 + V3 imza şemaları. Sadece V3 hata verir.**

```bash