
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Security_Android Apk Hardening_References_Faz 2 Sertle Tirme |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Faz 2 — Sertleştirme

Kırılganlık haritasındaki her maddeyi bir savunmayla eşle.

### İlke 1: Client'a Güvenme (Temel Kural)

Client tarafı kod cihazda çalışır, cihaz kullanıcının elindedir. Her client-side kontrol nihayetinde atlatılabilir.

**DOĞRU:** Premium kararını client'ta verme. Korunan işlevin kendisini sunucuya taşı.
**YANLIŞ:** Client'ta `if (premium) { showFeature() }` — o if satırı yamanır.

```java
// KÖTÜ — client'ta karar
if (isPremium) { showPremiumFeature(); }

// İYİ — premium özellik sunucudan gelir
api.getPremiumData(token).enqueue(response -> {
    // response zaten yetkilendirilmiş, client karar vermez
    showData(response);
});
```

Atlanan bir if bloğu, sunucuda olmayan veriyi var edemez.

### İlke 2: Server-side Doğrulama

Lisans/abonelik durumu sunucuda tutulur. Client her oturumda kısa ömürlü bir token ile kendini doğrular.

```
Akış:
1. Client → Sunucu: "ben premium'um, işte token"
2. Sunucu → Google Play Developer API: "bu token geçerli mi?"
3. Google → Sunucu: "geçerli / değil"
4. Sunucu → Client: premium veri (veya hata)

NOT: Client'tan gelen "satın aldım" iddiasına asla doğrudan güvenme.
```

Google Play Billing için:
```java
// Sunucu tarafında — Play Developer API ile doğrula
// purchases.subscriptions.get(packageName, subscriptionId, token)
// Client'tan gelen purchase token'ı sunucuda doğrula
```

### İlke 3: Play Integrity API — Doğru Entegrasyon

**Kritik nokta:** Integrity verdict'i client'ta değil, **sunucuda** doğrulanmalı.

```
DOĞRU AKIŞ:
1. Sunucu bir nonce üretir → client'a gönderir
2. Client nonce'u Integrity API'sine verir
3. Integrity API imzalı token döndürür
4. Client token'ı sunucuya iletir
5. Sunucu token'ı Google ile çözer ve doğrular
6. Nonce eşleşiyor mu? Cihaz bütünlüğü yerinde mi? → Karar sunucuda

YANLIŞ:
if (integrityOk) { ... }  ← Bu if'i atlatmak yine tek satır
```

Nonce server-side üretildiği ve token server-side çözüldüğü için replay ve client-yamasına dayanıklı.

### İlke 4: Anti-Tamper (Gerçekçi Beklentiyle)

Bunlar caydırıcıdır, mutlak değil. Amaç çıtayı yükseltmek, kırmayı imkansız kılmak DEĞİL.

#### 4a — İmza Doğrulama

Uygulama çalışırken kendi imza sertifikası hash'ini kontrol eder. Yeniden paketlenip başka anahtarla imzalanmışsa fark eder.

```java
private boolean checkSignature(Context ctx) {
    String validHash = "a1:b2:c3:..."; // gerçek hash
    try {
        PackageInfo pkg = ctx.getPackageManager()
            .getPackageInfo(ctx.getPackageName(),
                PackageManager.GET_SIGNATURES);
        String currentHash = hash(pkg.signatures[0].toByteArray());
        return validHash.equals(currentHash);
    } catch (Exception e) {
        return false;
    }
}
```

**UYARI:** Bu kontrolün kendisi de smali'de bir yer olduğundan, tek başına yeterli değil. Sunucuya bildiren bir yapıyla birleştir (imza hash'i sunucuda da doğrulanabilir veya imza başarısızsa sunucuya rapor gönder).

#### 4b — R8/ProGuard Obfuscation

Sınıf/metot adlarını anlamsızlaştırır, jadx çıktısını okumayı ciddi zorlaştırır. Bedava ve etkili ilk savunma.

```gradle
// build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

Bir APK'yı R8 ile küçültüp sonra jadx'te açmayı dene — farkı göreceksin.

#### 4c — Kontrol Noktalarını Çoğalt ve Dağıt

Tek `isPremium()` yerine kararı birden çok yere böl. Saldırganın her birini bulup yaması gerekir.

```java
// KÖTÜ — tek nokta
if (licenseManager.isPremium()) { showFeature(); }

// İYİ — dağıtık kontrol
if (licenseManager.isPremium() &&
    integrityCheck.passes() &&
    serverToken.isValid()) {
    showFeature();
}
```

Saldırgan üçünü de bulup yamamalı. Caydırıcılık artar.

#### 4d — Kritik Mantığı NDK/Native'e Taşı

.so içindeki C/C++ kodu apktool ile decompile edilmez, sadece zorlu disassembly ile okunur (Ghidra, IDA).

```cpp
// native-lib.cpp
extern "C" JNIEXPORT jboolean JNICALL
Java_com_app_NativeLicense_check(JNIEnv* env, jobject thiz, jstring input) {
    // Java'da görünmeyen lisans mantığı
    // Derin obfuscation + anti-debug
    return verify(input); // true/false
}
```

**Seviyeler:**
- Java'da kontrol → apktool/jadx ile 5 dk
- Native'de kontrol → Ghidra ile saatler
- Native'de obfuscated + anti-debug → günler

### Tehdit Modelini Netleştir

Şunu kabul et: kararlı bir saldırgan, cihazda çalışan her şeyi eninde sonunda aşabilir (root + Frida dinamik enstrümantasyon + GPT ile analiz).

**Gerçek güvenlik sınırın sunucu.** Anti-tamper'ın işi:
- Saldırıyı imkânsız kılmak değil
- Pahalı ve kırılgan kılıp çoğu kullanıcı için caydırmak

---