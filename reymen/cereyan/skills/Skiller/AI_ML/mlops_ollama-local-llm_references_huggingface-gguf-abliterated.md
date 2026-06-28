---
name: mlops_ollama-local-llm_references_huggingface-gguf-abliterated
description: HuggingFace GGUF Abliterated Model Import
title: "Mlops Ollama Local Llm References Huggingface Gguf Abliterated"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | HuggingFace GGUF Abliterated Model Import |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# HuggingFace GGUF Abliterated Model Import

## Referans Zincir

Abliterated (refusal katmanı kaldırılmış) modeller için tipik HF zinciri:

```
Orijinal Firma Modeli
  → roslein/<model>-abliterated (safetensors, abliterated)
    → mradermacher/<model>-abliterated-GGUF (GGUF quantizations)
```

## Qwen3-32B-abliterated (Haziran 2028)

| Adım | Repo | Format |
|------|------|--------|
| Orijinal | Qwen/Qwen3-32B | Safetensors |
| Abliterated | roslein/Qwen3-32B-abliterated | Safetensors (14 parça, 65.5 GB) |
| GGUF | mradermacher/Qwen3-32B-abliterated-GGUF | GGUF (11 quant seçeneği) |

### Mevcut GGUF Quantları (mradermacher)

| Quant | Yaklaşık Boyut | 32GB RAM? | Kalite |
|-------|---------------|-----------|--------|
| IQ4_XS | ~18 GB | ✅ Rahat | İyi |
| Q2_K | ~13 GB | ✅ Rahat | Düşük |
| Q3_K_S | ~15 GB | ✅ Rahat | Orta |
| Q3_K_M | ~16 GB | ✅ Rahat | Orta+ |
| **Q3_K_L** | **~17 GB** | **✅ Rahat** | **İyi** |
| **Q4_K_S** | **~19 GB** | **✅** | **İyi+** |
| **Q4_K_M** | **~20 GB** | **✅** | **En iyi denge** |
| Q5_K_S | ~22 GB | ⚠️ Sınırda | Çok iyi |
| Q5_K_M | ~24 GB | ❌ Taşar | Çok iyi |
| Q6_K | ~28 GB | ❌ Taşar | Mükemmel |
| Q8_0 | ~34 GB | ❌ Taşar | Orijinal |

### Kurulum

```bash
# Q4_K_M (önerilen — 32GB RAM için en iyi denge)
ollama create qwen3:32b-abliterated ^
  --from "https://huggingface.co/mradermacher/Qwen3-32B-abliterated-GGUF/resolve/main/Qwen3-32B-abliterated.Q4_K_M.gguf" ^
  --template "{{ .Prompt }}"

# Veya Modelfile ile
# Modelfile içeriği:
#   FROM Qwen3-32B-abliterated.Q4_K_M.gguf
#   TEMPLATE "{{ .Prompt }}"
#   PARAMETER num_ctx 32768
#
# ollama create qwen3:32b-abliterated -f Modelfile

# Doğrulama
ollama list
ollama run qwen3:32b-abliterated "Merhaba, kendini tanıtır mısın?"
```

### Daha Küçük Alternatifler

- `huihui-ai/Huihui-Qwen3-VL-32B-Instruct-abliterated` — Görsel + metin (33B)
- `mradermacher/Qwen3-32B-abliterated-i1-GGUF` — i1 varyantı (farklı abliteration metodu)

### Uyarılar

- İndirme süresi: Q4_K_M ~20 GB → 50 Mbps'de ~55 dk
- Ollama 0.30.8'de `--from` URL ile direkt import çalışır
- Abliterated modellerde kalite kaybı olabilir (özellikle nadir dillerde)
- Apache-2.0 lisansı ile dağıtılır
