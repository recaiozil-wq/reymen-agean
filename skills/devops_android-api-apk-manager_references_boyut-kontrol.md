
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_Boyut Kontrol |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Boyut kontrolü
ls -la signed.apk
```

#### 9. Kullanıcıya Teslim Et

**Fallback zincirini kullan:** Yukarıdaki "APK Dosyasını Telefona Aktarma (Fallback Zinciri)" bölümüne bak. Sırasıyla:
1. ADB dene
2. USB Debugging açtır
3. Telegram 9MB parçalı gönder
4. Kullanıcı yapamıyorsa, en kolay yöntemi seç (genelde Telegram parçalı gönder)

**Windows APK'yı zip gibi açma sorunu:** Windows bazen .apk dosyasını zip arşivi olarak tanır. Kullanıcı "Apk dosya degil bunlar" derse: kısa isimle tekrar masaüstüne kopyala veya .zip içinde gönder.

### Pitfall'lar (APK Modding)

1. **apktool rebuild binary XML bozabilir** — "Paket geçersiz göründü" hatası alınırsa: ya aapt2 ile direkt derle (apktool yerine) ya da orijinal APK'yı koruyup sadece smali seviyesinde değişiklik yap
2. **Native lib sıkıştırması** — apktool build lib'leri sıkıştırır. `extractNativeLibs="false"` ise Android açamaz. İkisini uyumlu yap: `extractNativeLibs="true"` veya build sonrası lib'leri uncompressed olarak yeniden paketle
3. **V3-only imza** — Android 16 bazen sadece V3 imzalı APK'yı reddeder. `apksigner` ile V2+V3 birlikte imzala
4. **Split APK** — apktool base + split olarak üretebilir. Single APK için `isSplitRequired` temizlenmeli veya APKEditor ile birleştirilmeli
5. **targetSdk 36 (Android 16)** — kullanma, 35 (Android 15) daha güvenilir. 36 yeni kısıtlamalar getirir
6. **Foreground Service + Mikrofon** — Android 16, RECORD_AUDIO + FOREGROUND_SERVICE kombinasyonunu stalkerware olarak algılayıp UI kurulumunu engeller. ADB ile sideload tek çözüm
7. **APK boyutu büyükse** — 15MB+ APK'ları Telegram'a MEDIA: ile gönderirken timeout olabilir. Güvenilir yöntem: 9MB parçalara bölüp (`split -b 9M`), her parçayı ayrı `send_message(target='telegram')` ile gönder. Bu yöntem 27MB APK'da bile çalışır.
8. **Windows APK ekstraksiyonu** — Kullanıcı APK'yı zip gibi açıp içindekileri görebilir. APK dosyasının kendisini kullanması gerektiğini belirt

### Samsung / One UI 8 / Android 16 Sideload Sorun Giderme

**Belirti**: APK yüklenmeye çalışırken Google Play Protect "engellendi" diyor,
"Anladım" butonuna basınca "Uygulama yüklenmedi" hatası alınıyor.

**Sebep**: 2026 itibarıyla Google + Samsung çift katman güvenlik:
1. **Google Play Protect** — bilinmeyen geliştirici imzasını engeller
2. **Samsung Auto Blocker** (One UI 8) — Knox tabanlı ek güvenlik
3. **Android 16** — yeni kurulum kısıtlamaları, hedef SDK kontrolü
4. **Android 16 Stalkerware Detection** — FOREGROUND_SERVICE + RECORD_AUDIO kombinasyonu yükleme zamanında tespit edilip engellenir (Play Protect ve Auto Blocker'dan bağımsız). Detay: `references/android16-stalkerware-detection.md`

### Samsung Cihaz Bilgisi Tespiti

Kullanıcı "Telefonunuzla uyumlu değil" hatası alıyorsa, önce cihaz modelini tespit et:

```bash