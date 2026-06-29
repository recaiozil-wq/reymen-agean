--- 
title: Metin Özetleme Aracı
name: metin-ozetleme
description: Uzun metinleri, makaleleri ve dokümanları anlamlı özetlere dönüştürür
tags: [nlp, ozet, metin, dokuman, extractive]
---

# Metin Özetleme Aracı

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Uzun metinleri, logları, makaleleri ve dokümanları kısa ve anlamlı özetlere dönüştürür |
| Nerede | reymen/cereyan/skills/Skiller/AI_ML/nlp/ |
| Ne Zaman | Uzun bir metnin hızlıca anlaşılması gerektiğinde |
| Neden | Zaman kazanmak ve büyük hacimli bilgiyi hızlıca kavramak için |
| Nasıl | LLM çağrısı ile extractive+abstractive karma özetleme yapılır |

## Özetleme Modları

| Mod | Açıklama | Kullanım |
|-----|----------|----------|
| Extractif | Önemli cümleleri aynen seç | Log analizi, hukuk metni |
| Abstractif | Yeni cümlelerle yeniden yaz | Blog, haber makalesi |
| Hibrit | %70 extract + %30 rewrite | Genel amaçlı |
| Soru-Cevap | Özet yerine sorulara yanıt | Eğitim, hızlı tarama |

## Adımlar

1. Metni paragraflara böl
2. Her paragraftan anahtar cümleleri çıkar
3. LLM ile tutarlı bir özete dönüştür
4. Özeti hafızaya kaydet (`nlp/ozet` kategorisi)
