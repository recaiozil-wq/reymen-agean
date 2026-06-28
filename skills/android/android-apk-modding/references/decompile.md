---
skill_id: 40d7fa7f29a8
usage_count: 1
last_used: 2026-06-16
---
# Decompile
$APKTOOL d -f -o _work/ target.apk
```

**GATE 1:**
```bash
[ -f _work/AndroidManifest.xml ] && echo "MANIFEST_OK" || echo "MANIFEST_FAIL"
[ -d _work/smali ] && echo "SMALI_OK" || echo "SMALI_FAIL"
```

İkisi de OK değilse DUR. apktool sessizce başarısız olmuştur — farklı bir sürüm dene veya APK bozuk.

---

### Adım 2 — YAMA (Karar Ağacı)

Ne tür değişiklik yapılacağını belirle, alt-yordamı seç:

```
Kullanıcının isteği nedir?
├── Manifest değişikliği (izin, servis, debuggable, targetSdk)
│   → ALT-YORDAM: manifest-patch
├── Resource değişikliği (renk, yazı, logo, string)
│   → ALT-YORDAM: resource-patch
└── Smali/davranış değişikliği (yeni özellik, service start, hook)
    → ALT-YORDAM: smali-patch
```

#### ALT-YORDUM: manifest-patch

`_work/AndroidManifest.xml` düz XML — doğrudan düzenle.

Sık yapılanlar:

```xml
<!-- debuggable aç -->
<application android:debuggable="true" ...

<!-- network security config -->
<application android:networkSecurityConfig="@xml/network_security_config" ...

<!-- izin ekle -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE"/>

<!-- split APK referanslarını sil -->
<!-- manifest <manifest> tag'inden şunları kaldır: -->
android:isSplitRequired
android:requiredSplitTypes
android:splitTypes
<!-- meta-data'dan kaldır: -->
splits.required
com.android.vending.splits
```

targetSdk düşürmek için `_work/apktool.yml`:
```yaml
sdkInfo:
  targetSdkVersion: 35   # 36→35
```

**GATE 2M:** `grep "yaptığın değişiklik" _work/AndroidManifest.xml`

#### ALT-YORDUM: resource-patch

- Logo değiştir: `_work/res/drawable/` veya `res/mipmap-*/`
- Renk değiştir: `_work/res/values/colors.xml` — hex value bul ve değiştir
- String değiştir: `_work/res/values/strings.xml`
- Resource ID teyit: `grep "icon\|logo\|splash" _work/res/values/public.xml`

**GATE 2R:** Eski resource artık yok mu? Yeni resource public.xml'de var mı?

#### ALT-YORDUM: smali-patch

**Önce en basit teknik: onPause/onStop Boşaltma**

Kullanıcı "ekran kilitlenince kaydı durdurma" gibi tek bir davranışı kapatmak istediğinde, yeni service/hook ekleme. En hızlı çözüm: Activity'nin onPause() veya onStop() metodundaki kodları silmek.

Adımlar:
1. Activity'de `onPause()` metodunu bul (obfuscated da olsa `invoke-super.*onPause` aranır)
2. Metot içinde transcription/kayıt durduran çağrıları tespit et
3. Metodu sadece `invoke-super` + `return-void` bırak — aradaki tüm kodları sil
4. `.locals` değerini 0'a düşür (eski register sayısından)
5. Aynı kontrolü `onStop()` için de yap — bazı uygulamalar onStop'u kullanır

```smali
.method protected final onPause()V
    .locals 0

    .line 1
    invoke-super {p0}, Lfzv;->onPause()V

    .line 2
    return-void
.end method
```

Bu teknik uygulama minimize edildiğinde/kilitlendiğinde kaydın devam etmesini sağlar. İstenmeyen yan etki: kullanıcı uygulamadan çıkınca da kayıt devam eder.

**İleri teknik — obfuscated APK'lerde yeni sınıf ekleme:**

Obfuscated APK'lerde sınıf isimleri a, b, c olur. Mevcut smali'yi anlamaya çalışma. Sadece ya yeni sınıf ekle (karmaşık) ya da onPause boşalt (basit).

**Yeni smali sınıfı ekleme şablonu (basic KeepAliveService):**

```smali