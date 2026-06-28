
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Security_Android Apk Hardening_References_Faz 1 Apk Y Sald Rgan G Z Yle Oku |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Faz 1 — APK'yı Saldırgan Gözüyle Oku

Amaç yama yapmak değil, "lisans/premium mantığım ne kadar görünür ve ne kadar tek-noktaya bağlı?" sorusunu yanıtlamak.

### 1a — jadx ile Java seviyesinde analiz

jadx-gui ile APK'yı aç, decompile edilmiş Java kodunu oku. Aradığın şeyler:

```bash
jadx-gui app.apk
```

- `isPremium()`, `checkLicense()`, `isPro()`, `hasSubscription()` gibi metot isimleri
- `if (valid) { unlock() }` deseni — tek satırlık yamaya açık
- `SharedPreferences.getBoolean("premium", false)` — kolay atlatılır
- `BuildConfig.PREMIUM` veya `BuildConfig.DEBUG` — derleme sabiti, en kolayı

**KIRMIZI BAYRAK — Tek nokta:** jadx'te gördüğün tek bir boolean kararı, saldırganın da göreceği ilk şeydir. Tek satırlık `if-eqz → if-nez` smali değişikliğiyle kırılır.

**GATE:** jadx çıktısında lisans/premium kararının yeri tespit edildi mi? Kaç noktada karar veriliyor?

### 1b — apktool ile smali'ye in

```bash
apktool d app.apk -o _audit/
```

Kontrol noktası sayısı:
- Tek metot mu (`isPremium()` → return boolean)?
- Birden çok yere dağılmış mı (her premium özellik ayrı kontrol)?
- SharedPreferences'tan mı okuyor (kolay)?
- Her açılışta sunucudan mı doğruluyor (zor)?
- Root check var mı? Varsa nerede?

```bash