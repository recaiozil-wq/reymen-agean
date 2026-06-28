
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Dot Format Class Forname Com Eski Paket Class |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Dot format (Class.forName("com.eski.paket.Class"))
grep -rl "com.eski.paket" smali/ smali_classes2/ | \
  xargs sed -i 's/com\.eski\.paket/com.yeni.paket/g'
```
`.class public Lcom/eski/...;` satırı da değişmeli — yoksa `ClassNotFoundException`.

**4) Layout XML'de custom view isimlerini değiştir**
```bash
grep -rl "com.eski.paket" res/ | xargs sed -i 's/com\.eski\.paket/com.yeni.paket/g'
```
Layout inflater tam nitelikli sınıf adıyla yükler (`com.eski.paket.ui.CustomView`).

**5) Permission + Provider string'lerini düzelt**
```bash
sed -i 's/com\.eski\.paket/com.yeni.paket/g' _work/AndroidManifest.xml
```
Düzeltilmezse: `INSTALL_FAILED_DUPLICATE_PERMISSION` veya `INSTALL_FAILED_CONFLICTING_PROVIDER`.

**6) (Opsiyonel) Binary raw/protobuf dosyaları**
AYNI UZUNLUKTA string replacement protobuf'u bozmaz:
```bash
sed -i 's|com/eski/paket|com/yeni/paket|g' res/raw/*
```

**7) Split APK referanslarını manifest'ten temizle**
```xml
<!-- sil: -->
android:requiredSplitTypes="base__abi"
android:splitTypes=""
<meta-data android:name="com.android.vending.splits.required" .../>
<meta-data android:name="com.android.vending.splits" .../>
```

**8) onPause/onStop boşalt (hedef buysa)**
MainActivity'de onPause metodunu bul, invoke-super + return-void dışındaki tüm satırları sil.

**9) İmzala + yükle**
```bash
apksigner sign --ks release.keystore --ks-key-alias alias --ks-pass pass:sifre _build_aligned.apk
adb install _build_aligned.apk
```

**10) LauncherActivity'yi aktifleştir** (rename yapılan uygulamalarda)
Sistem uygulamalarında LauncherActivity alias genelde `android:enabled="false"` olur. Sideload'da bu aktif olmadığı için uygulama menüde görünmez:
```xml
<activity-alias android:enabled="true"  <!-- false → true -->
  android:exported="true"
  android:name="com.yeni.paket.LauncherActivity"
  android:targetActivity="com.yeni.paket.MainActivity">
```
Aktifleştirilmezse `monkey -p com.yeni.paket 1` çıktısı: "No activities found to run, monkey aborted."

**11) logcat ile doğrula**
```bash
adb logcat -c && adb shell am start -n com.yeni.paket/.MainActivity
sleep 8 && adb logcat -d | grep -E "FATAL|CRASH|AndroidRuntime"
```

#### Olası Crash'ler

| Hata | Sebep | Çözüm |
|------|-------|-------|
| `ClassNotFoundException: com.ESKI.paket.Class` | Smali'de class reference değişmemiş | `Class.forName()` string'lerini kontrol et |
| `ClassNotFoundException: com.YENI.paket.Class` | Layout'ta custom view eski kalmış | `res/layout/*.xml` kontrol et |
| `INSTALL_FAILED_DUPLICATE_PERMISSION` | Permission name eski pakette | `<permission android:name>` değiştir |
| `INSTALL_FAILED_CONFLICTING_PROVIDER` | Provider authority eski | `<provider android:authorities>` değiştir |

**ERKEN ÇIKIŞ (ÖNEMLİ):** Smali'de `isPremium()`, `checkLicense()` gibi boolean dönüş yoksa, sadece `fetchPremiumData()` → HTTP POST → null/JSON deseni varsa, bu APK **server-side yetkilendirme** kullanıyordur. Bu durumda yama yapılamaz — `android-apk-hardening` skill'ine yönlendir.

**GOOGLE APPS — Sunucu Taraflı İmza Kontrolü (KRİTİK İSTİSNA):**

Google uygulamalarını (`com.google.*`) modlamak APK seviyesinde çalışsa bile **sunucu tarafında çalışmaz.** Google sunucuları (gRPC, Firebase, Cloud Speech API) uygulama imzasını doğrular. Custom keystore ile imzalanan APK'yı sunucu reddeder.

| Hizmet | Davranış |
|--------|----------|
| **Google Cloud Speech (Live Transcribe)** | Mikrofon açılır, ses alınır, sunucuya giderken imza hatası → "INVALID_ARGUMENT: credential not valid" → transcription session kapanır |
| **Firebase Instance ID** | `Failed to retrieve Firebase Instance Id` — imza eşleşmezse Firebase auth çalışmaz |
| **Firebase Auth / Google Sign-In** | Custom imzalı APK ile Google hesabına bağlanılamaz |

**Kural:** Eğer uygulama cloud tabanlı konuşma tanıma (speech-to-text), canlı altyazı, voice search gibi Google sunucu hizmetlerini kullanıyorsa → **package rename + custom imza ile çalışmaz.**

**İstisnalar:** Offline-only özellikler (önceden indirilmiş dil modelleri, TF Lite ile lokal çalışan modeller) kaynak uygulamada varsa çalışabilir. Ama Live Transcribe'da tüm transkripsiyon sunucu taraflıdır, TF Lite modelleri sadece ses sınıflandırma (sound events) içindir.

**Alternatif stratejiler:**
- Root + sistem bölümüne yama: Orijinal imza korunur, sunucu kabul eder
- Frida hook (root gerekir): APK'ya dokunulmaz, imza bozulmaz. Ancak Android 16+ One UI 8'de non-root cihazlarda Frida system app'lere bağlanamaz (attached failed → spawn failed → root gerekir)
- Root'suz çözüm yok: cloud tabanlı Google uygulamaları modlanamaz

---



### Adım 1 — DECOMPILE

```bash