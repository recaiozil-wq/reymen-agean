--- 
title: Nesne Tespiti ve Takibi
name: nesne-tespiti
description: Video ve görsellerdeki nesneleri tespit eder, sınır kutularıyla işaretler ve takip eder
tags: [vision, nesne, tespit, takip, bounding-box]
---

# Nesne Tespiti ve Takibi

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Görsellerdeki ve videolardaki nesneleri tespit eder, sınır kutuları çizer |
| Nerede | reymen/cereyan/skills/Skiller/AI_ML/vision/ |
| Ne Zaman | Güvenlik kamerası, trafik analizi veya envanter sayımı gibi görevlerde |
| Neden | Görsel ortamda belirli nesnelerin varlığını ve konumunu otomatik tespit etmek için |
| Nasıl | YOLO/ResNet benzeri mimari veya vision LLM ile bounding box çıkarılır |

## Tespit Formatı

```json
{
  "nesneler": [
    {"etiket": "insan", "guven": 0.95, "bbox": [120, 45, 300, 400]},
    {"etiket": "araba", "guven": 0.87, "bbox": [50, 200, 250, 150]}
  ],
  "cozumlenme_suresi": 1.2
}
```

## Kullanım Adımları

1. Görsel/video karesini modele gönder
2. Tespit edilen nesneleri bounding box + güven skoru ile al
3. Güven eşiği altındakileri filtrele (varsayılan: 0.5)
4. Sonuçları hafızaya kaydet (`vision/nesne/` kategorisi)
5. İstenirse video karesi üzerinde görselleştir
