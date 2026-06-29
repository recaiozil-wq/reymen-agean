---
name: software-development_android-native-app-builder_references_sonra-uygulamay-yeniden-ba-lat
description: "Sonra uygulamayı yeniden başlat:"
title: "Software Development Android Native App Builder References Sonra Uygulamay Yeniden Ba Lat"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Sonra uygulamayı yeniden başlat: |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Sonra uygulamayı yeniden başlat:
adb shell am force-stop com.package
adb shell am start -n com.package/.MainActivity
```
Bu yöntemle izin dialogları hiç gösterilmez, doğrudan BAŞLAT'a basabilirsin.

**Pitfall:** Emülatörün sanal mikrofonu olmadığı için BAŞLAT'a basınca SpeechRecognizer hemen hata döner ve duruma yansımaz. Test için "Butonlara basılabiliyor ve durum değişiyor" yeterlidir.

### Ekran Görüntüsü (Emülatör)
```bash
