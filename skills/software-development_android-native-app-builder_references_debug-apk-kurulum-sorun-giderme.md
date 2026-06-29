---
name: software-development_android-native-app-builder_references_debug-apk-kurulum-sorun-giderme
description: Debug APK Kurulum Sorun Giderme
title: "Software Development Android Native App Builder References Debug Apk Kurulum Sorun Giderme"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Debug APK Kurulum Sorun Giderme |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Debug APK Kurulum Sorun Giderme

Debug APK (debug imzalı) fiziksel telefona yüklenemiyorsa:

### Yaygın Sebepler

| Sorun | Çözüm |
|-------|-------|
| **Bilinmeyen kaynaklar kapalı** | Ayarlar > Güvenlik > Bilinmeyen uygulamalar > AÇIK |
| **Geliştirici seçenekleri kapalı** | Ayarlar > Telefon hakkında > Derleme numarasına 7 kere tıkla → Geliştirici seçenekleri > USB hata ayıklama + USB üzerinden kurulum AÇIK |
| **Telegram'dan bozuk indi** | Telegram bot'tan APK'yı sil, tekrar gönder, yeniden indir |
| **Aynı paket adıyla başka uygulama var** | Eski sürümü kaldır (varsa) |
| **Samsung Auto Blocker (One UI 8+)** | Ayarlar > Güvenlik > Auto Blocker > KAPAT. Debug APK'yi direkt engeller. Release imzalı APK yap veya Auto Blocker'ı kapat. |
| **Android 16 sideload kısıtlaması** | Bilinmeyen kaynaklar iznini Telegram/My Files uygulamasına özel olarak ver. Ayarlar > Uygulamalar > [Uygulama] > Bilinmeyen uygulamaları yükle > İzin ver. |
| **APK bozuk** | `aapt2 dump badging app.apk` ile doğrula — çıktıda `package:` ve `minSdkVersion:` satırları görünmeli |

### Doğrulama

```bash
