--- 
title: Ses Sentezleme Asistanı
name: ses-sentezleme
description: Metinleri doğal sese dönüştürür, ses tonu ve hız ayarları yapar
tags: [medya, ses, tts, ses-sentez, konusma]
---

# Ses Sentezleme Asistanı

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Yazılı metinleri doğal insan sesine dönüştürür, ses tonu ve hızını ayarlar |
| Nerede | reymen/cereyan/skills/Skiller/Medya/ |
| Ne Zaman | Sesli yanıt, podcast veya sesli kitap üretimi gerektiğinde |
| Neden | Metin tabanlı içeriği sesli formata çevirerek erişilebilirliği artırmak için |
| Nasıl | OpenAI TTS veya benzeri API ile ses dosyası oluşturulur |

## Ses Parametreleri

| Parametre | Değerler | Varsayılan |
|-----------|----------|------------|
| Ses (voice) | alloy, echo, fable, onyx, nova, shimmer | nova |
| Hız (speed) | 0.25 - 4.0 | 1.0 |
| Format | mp3, opus, aac, flac, wav | mp3 |

## Kullanım Akışı

1. Metni paragraflara böl (max 4096 karakter/her çağrı)
2. Her paragraf için TTS çağrısı yap
3. Ses dosyalarını birleştir (ffmpeg ile)
4. Çıktıyı `Medya/ses/` altına kaydet
5. Hafızaya referans ekle (`medya/ses/tts`)
