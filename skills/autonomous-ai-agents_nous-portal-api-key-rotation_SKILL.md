---
name: autonomous-ai-agents-nous-portal-api-key-rotation
description: Autonomous Ai Agents Nous Portal Api Key Rotation skill for AI/ML operations.
title: Autonomous Ai Agents Nous Portal Api Key Rotation
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

Nous Portal üzerinden API anahtarı üretme, iptal etme ve Hermes .env’e
#Nous Portal API Key Rotation
## Amaç
Nous Portal’dan anahtar ürettikten sonra bunu Hermes’in doğru okuyacağı
 `.env` değişkenine yazmak ve “yanlış değişken adı” tuzağından kaçınmak.
## Doğru değişken adı
- Provider DeepSeek üzerinden yapılandırıldıysa kullanılacak env: `DEEPSEEK_API_KEY`
- `NOUS_API_KEY` şu anki Hermes yapılandırmasında okunmuyor.
  Bu değişkene ne kadar anahtar yazarsanız, körü körüne atlanır.
## Neden bazen geçersiz anahtarla 401 alınıyor?
- Portalda üretilen anahtarın numunesi/aktif olmaması.
- Kullanıcının portalda var olan ama kredisi bitmiş/iptal edilmiş anahtarı
  yeniden denemesı.
- Anahtarın `.env` değil, config.yaml gibi başka yere yapıştırılması.
##Kurallar
1. Yeni anahtar üretildiyse sadece `.env` dosyasına yaz.
2. Yapı: config.yaml => provider, base_url vs.
3. .env => sadece API key.
4. Hermes’te gözüken anahtar maskelenir; yayma.
5. Değişiklikten sonra oturumu yenile.
## .env yolu
- Windows: `C:\Users\<user>\AppData\Local\hermes\.env`
## Doğrulanma
```bash
hermes status
```
Model/Provider ve API key satırlarını kontrol et. Endpoint 200 dönüyorsa başarılı.
## Kalıcı öğrenme
- Yanlış değişken adı: `NOUS_API_KEY` yerine `DEEPSEEK_API_KEY`
- Geçersiz anahtarlar: portalda önce aktif olduğundan emin ol.
- Çözüm anahtarı: doğru değişken adı + aktif anahtar.
