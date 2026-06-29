---
name: mlops_lm-studio_references_qwen3-32b-vs-dolphin-8b
description: Qwen3-32B-obliterated vs Dolphin 3.0 8B — Karşılaştırma (2026-06-13)
title: "Mlops Lm Studio References Qwen3 32B Vs Dolphin 8B"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Qwen3-32B-obliterated vs Dolphin 3.0 8B — Karşılaştırma (2026-06-13) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Qwen3-32B-obliterated vs Dolphin 3.0 8B — Karşılaştırma (2026-06-13)

## Donanım

- GPU: RTX 4070 Laptop (4GB VRAM)
- RAM: 32 GB
- İşlemci: laptop CPU

## Qwen3-32B-obliterated.i1-Q5_K_M.gguf (23.2 GB)

**Yükleme:** `lms load qwen3-32b-obliterated-i1 --gpu 0.5 -y --identifier qwen3-32b`
- Süre: 59 saniye
- RAM: 21.62 GiB kullanım
- GPU offload: %50 (CUDA)
- llama.cpp 2.22.0 (nvidia-cuda-avx2)

**Test sonucu:**
- Inference çalışıyor, reasoning içeriği görüntüleniyor
- Token/s: çok düşük (~15-30 sn/token)
- 150 token için 5+ dakika bekledi
- `finish_reason: "length"` — max_tokens'a takıldı, content hep boş
- Pratik kullanım için uygun DEĞİL

## Dolphin 3.0 8B (Q4_K_S, ~4.69 GB)

**Yükleme:** Önceden yüklenmişti (`cognitivecomputations.dolphin3.0-llama3.1-8b`)
- RAM: ~5 GB kullanım
- GPU'da tamamen çalışıyor (4GB VRAM yeterli)

**Test sonucu:**
- 13 token yanıt, ~2 saniye
- `finish_reason: "stop"` — tam cevap
- Merhaba! Bu yıl 2023'tür.
- ❗ Eğitim verisi 2023'e kadar — güncel bilgi istendiğinde uyar

## Dersler

1. 4GB VRAM için 7B-8B modeller idealdir
2. 32B modeller CPU'da çalışır, 100x yavaş
3. Reasoning modeller (Qwen3, DeepSeek-R1) token limitini hızlı tüketir
4. Q5_K_M quant 23GB → 32B için bile büyük; Q4_K_M daha iyi olabilir
5. "obliterated.i1" GGUF formatı (Imroz-1) llama.cpp 2.22.0 ile uyumlu
