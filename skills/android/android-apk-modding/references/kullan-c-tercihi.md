---
skill_id: 562f7c1ef412
usage_count: 1
last_used: 2026-06-16
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