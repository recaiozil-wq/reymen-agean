---
name: seq2seq-design
description: Seq2Seq Design skill for AI/ML operations.
title: Seq2Seq Design
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

Given a task (translation, summarization, paraphrase, question rewrite), output:
1. Architecture. Pretrained transformer encoder-decoder (BART, T5, mBART, NLLB) is the default. RNN-based seq2seq only for specific constraints (streaming, edge inference, pedagogy).
2. Starting checkpoint. Name it (`facebook/bart-base`, `google/flan-t5-base`, `facebook/nllb-200-distilled-600M`). Match checkpoint to task and language coverage.
3. Decoding strategy. Greedy for deterministic output, beam search (width 4-5) for quality, sampling with temperature for diversity. One sentence justification.
4. One failure mode to verify before shipping. Exposure bias manifests as generation drift on longer outputs; sample 20 outputs at 90th-percentile length and eyeball.
Refuse to recommend training a seq2seq from scratch for under ~1M parallel examples. Flag any pipeline using greedy decoding for user-facing content as fragile (greedy repeats and loops).
