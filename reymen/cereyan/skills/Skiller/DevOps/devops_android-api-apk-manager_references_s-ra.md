
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_S Ra |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Sıra
1) **Varlık kontrolü**
   - APK dosyalarını bul: `C:\Users\<user>\Downloads` ve varsa `Projects/android`
   - Yüklü uygulamaları listele: `adb shell pm list packages`
   - Eğer APK tarama scripti (`android_scan.py`) varsa çalıştır

2) **Eksikleri işaretle**
   - Temel Araçlar: `Files`, `Termux` (opsiyonel eklentiler)
   - Not: ekran kaydedici/screenshot için `screencap` kullan

3) **Kurulum**
   - Bulunan APK seç, `adb install -r <apk>` ile kur ya da APK dosyasını aç
   - Yanlış/corrupt APK bulursan başka bir APK dene

4) **Sonrası**
   - Yapılandırma tamamlandı mı kontrol et: run kullanarak test et
   - Cihazda yüklü paketleri doğrula: `adb shell cmd package ls packages`