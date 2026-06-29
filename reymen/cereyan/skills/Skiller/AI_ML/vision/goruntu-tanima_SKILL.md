--- 
title: Görüntü Tanıma ve Sınıflandırma
name: goruntu-tanima
description: Görsellerdeki nesneleri, metinleri ve desenleri tanıyarak kategorize eder
tags: [vision, goruntu, tanima, siniflandirma, ocr]
---

# Görüntü Tanıma ve Sınıflandırma

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Görselleri analiz eder, içindeki nesneleri, metinleri ve desenleri tanır |
| Nerede | reymen/cereyan/skills/Skiller/AI_ML/vision/ |
| Ne Zaman | Ekran görüntüsü, fotoğraf veya diyagram analizi gerektiğinde |
| Neden | Görsel bilgiyi yapılandırılmış veriye dönüştürmek ve otomatik kategorize etmek için |
| Nasıl | Vision LLM veya OCR tool ile görsel analiz edilir, sonuçlar hafızaya kaydedilir |

## Kullanım Senaryoları

| Senaryo | Araç | Çıktı |
|---------|------|-------|
| Ekran görüntüsü analizi | vision_analyze | UI element listesi |
| OCR (metin çıkarma) | vision_analyze + regex | Düz metin |
| Diyagram okuma | vision_analyze | Akış şeması (Mermaid) |
| Nesne tespiti | vision_analyze | Etiket + koordinat listesi |

## Hafıza Entegrasyonu

- `vision/analiz/screenshot` — ekran görüntüsü sonuçları
- `vision/analiz/ocr` — metin çıktıları
- `vision/kategori/` — sınıflandırma sonuçları

Her analiz sonucu 7 gün süreyle cache'de tutulur.
