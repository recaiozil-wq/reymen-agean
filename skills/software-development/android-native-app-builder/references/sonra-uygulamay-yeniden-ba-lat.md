---
skill_id: 952392db887d
usage_count: 1
last_used: 2026-06-16
---
# Sonra uygulamayı yeniden başlat:
adb shell am force-stop com.package
adb shell am start -n com.package/.MainActivity
```
Bu yöntemle izin dialogları hiç gösterilmez, doğrudan BAŞLAT'a basabilirsin.

**Pitfall:** Emülatörün sanal mikrofonu olmadığı için BAŞLAT'a basınca SpeechRecognizer hemen hata döner ve duruma yansımaz. Test için "Butonlara basılabiliyor ve durum değişiyor" yeterlidir.

### Ekran Görüntüsü (Emülatör)
```bash