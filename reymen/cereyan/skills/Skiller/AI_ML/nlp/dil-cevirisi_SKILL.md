--- 
title: Dil Çeviri Asistanı
name: dil-cevirisi
description: Metinleri farklı diller arasında çevirir, teknik terimleri korur ve bağlamı muhafaza eder
tags: [nlp, ceviri, dil, multilingual, localization]
---

# Dil Çeviri Asistanı

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Metinleri Türkçe, İngilizce, Almanca ve diğer diller arasında çevirir |
| Nerede | reymen/cereyan/skills/Skiller/AI_ML/nlp/ |
| Ne Zaman | Çok dilli içerik üretirken veya yabancı kaynak okurken |
| Neden | Teknik dokümanların ve kod yorumlarının dil bariyerini aşmak için |
| Nasıl | LLM ile bağlam koruyarak çeviri yapılır, teknik terimler sabitlenir |

## Çeviri Kuralları

| Kural | Açıklama |
|-------|----------|
| Teknik Terim | `function`, `variable`, `API` gibi terimler çevrilmez |
| Kod Blokları | Kod içeriği asla çevrilmez, sadece yorumlar |
| Markdown | Başlık, liste, tablo yapısı korunur |
| Bağlam | Paragraf bazında değil, doküman bütününde çeviri |

## Akış

1. Kaynak dili tespit et (langdetect veya LLM)
2. Hedef dili doğrula
3. Kod bloklarını ayır (dokunma)
4. Çeviriyi yap, teknik terimleri sabit tut
5. Çevrilmiş metni döndür + kaynak dili metadata'ya ekle
