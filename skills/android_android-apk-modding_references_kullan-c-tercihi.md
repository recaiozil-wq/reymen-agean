
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Kullan C Tercihi |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Kullanıcı Tercihi

**Önce en basit çözüm.** Karmaşık eklemeler (foreground service, yeni sınıf, hook) yapmadan önce:
1. Mevcut bir metodu boşaltmak yeterli mi? (onPause, onStop)
2. Manifest'te tek satır değişiklik çözüyor mu?
3. Resource/string değişiklik çözüyor mu?
Kullanıcı "sadece ayar değiştir" dediğinde direkt smali'deki ilgili metodu bul ve boşalt. Yeni özellik ekleme, yeni service yazma.

**Kısıtlı ortam (sistem uygulaması, imza koruması):**
Kullanıcı "bilinmeyen kaynaktan kod kullanılmayacak" dediğinde APK modding yapılamaz — sadece ADB komutları çalışır.
Bu durumda SDK izinleri (`appops`) ve Android sistem ayarları (`settings`, `pm`) dışında seçenek yok.