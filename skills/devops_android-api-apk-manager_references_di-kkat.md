
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_Di Kkat |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## DİKKAT
- `adb` ve OEM sürücüleri Windows 10'da yüklemek gerekir.
- Talimatlara göre ilerle; her aşamada durumu doğrula.
- Eğer bir araç yoksa önce onu bul/kur, sonra bir sonraki adıma geç.
- Güvenin bittiği adımları otomatik devam et.
- APK modding yaparken orijinal APK'yı yedekle.
- **Fallback zincirini kullan:** ADB önce, olmazsa USB Debugging açtır, olmazsa Telegram 9MB parçalı gönder. Sırayla dene.
- **"Ben beceremem" durumu:** Kullanıcı yapamayacağını söylerse en otomatik yöntemi seç (Telegram parçalı gönder). USB Debugging açtırmak için bile çok kısa adım yaz, uzun talimat verme.
- **Teslim:** Masaüstüne kopyala + Telegram parçalı gönder (ikisini birden yap). Biri çalışmazsa diğeri yedek olur.
- **"Yok" / "Olmadi" sinyali:** Kullanıcı "yok", "olmadi" dedikten sonra aynı yaklaşımı tekrar tekrar deneme. Yaklaşım değiştir. Kullanıcının önerdiği yeni yönü dene (örn. "telefon içinden değişiklik").
- **Telegram curl upload:** send_message MEDIA: timeout yiyorsa, curl ile direkt Telegram Bot API'ye yükle (token hex decode ile alınır). 30MB APK'lar sorunsuz çıkar.
- **Android 16 Stalkerware Detection:** FOREGROUND_SERVICE + RECORD_AUDIO kombinasyonu içeren APK'lar, kullanıcı arayüzü üzerinden **ASLA** kurulamaz. ADB sideload veya Play Store dağıtımı gerekir. Auto Blocker/Play Protect kapatmak işe yaramaz. Detay: `references/android16-stalkerware-detection.md`