
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Kt Varsa Si Stem Uygulamasi |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çıktı varsa = SİSTEM UYGULAMASI
```
Eğer sistem uygulamasıysa:
- `adb uninstall -k --user 0 <pkg>` ile kaldır
- Telefonu yeniden başlat (`adb reboot`)
- `adb install patched.apk` dene
- Hala `INSTALL_FAILED_UPDATE_INCOMPATIBLE` alınıyorsa → **Package rename stratejisine geç** (aşağıdaki bölüm)
- APK'yı telefona manuel kurmak için: push to `/data/local/tmp/`, `adb shell pm install -r -t /data/local/tmp/patch.apk`
- Sdcard'dan kurulum çalışmaz: `pm install` system_server olarak çalışır, sdcard'a erişemez

---

### SİSTEM UYGULAMASI BYPASS: Package Rename Stratejisi

Android 16+ One UI 8'de sistem uygulamalarına yama yapılamaz. Çözüm: **Paket adını değiştir, yeni bir uygulama olarak yükle.**

**ÖNEMLİ UYARI:** apktool'un `renameManifestPackage` özelliği SADECE manifest'teki `package=` attribute'unu değiştirir. **Smali class referanslarını, layout XML'deki custom view isimlerini, permission/provider string'lerini değiştirmez.** Bunların hepsini ayrıca elle yapman gerekir.

#### Full Workflow (Sistem Uygulaması Bypass)

**1) Yeni paket adı seç — AYNI UZUNLUKTA olmalı**
Binary AXML string pool'da offset'ler bozulmasın diye aynı karakter sayısı zorunlu:
```python
orig = "com.google.audio.hearing.visualization.accessibility.scribe"
new  = "com.transcribe.live.service.background.accessibility.extend"
assert len(orig) == len(new), f"Uzunluk farki: {len(orig)} vs {len(new)}"
```

**2) Decompile + apktool.yml ayarı**
```bash
apktool d -f -o _work/ merged_original.apk