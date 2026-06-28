---
name: asr-picker
description: Asr Picker skill for AI/ML operations.
title: Asr Picker
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

deployment target.
Given a deployment target (language list, domain, latency budget, hardware, offline / streaming, clip duration), output:
1. Model. Whisper-large-v3-turbo / Parakeet-TDT / Canary-Flash / wav2vec 2.0 / Moonshine. Reason in one sentence.
2. Decoding. Greedy / beam width / temperature fallback / LM fusion weight. Reason tied to the quality budget.
3. Chunking and VAD. Chunk length, stride, whether to gate with Silero-VAD or Whisper's own.
4. Language policy. Force language vs auto-LID; how to handle cross-lingual frames.
5. Eval plan. WER on domain test set, coverage-per-speaker, hallucination rate on silence clips.
Refuse any long-form Whisper deployment without VAD gating (hallucination-prone on silence). Refuse to report WER without text normalization (lower, punct strip). Flag any beam-width > 16 without an LM; raw beams over blanks do not help.
