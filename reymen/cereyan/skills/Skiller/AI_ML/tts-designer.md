---
name: tts-designer
description: Tts Designer skill for AI/ML operations.
title: Tts Designer
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

for a given language, style, and latency target.
Given a target (language(s), voice style, latency budget, CPU vs GPU, license constraints) and content (domain, OOV density, punctuation richness), output:
1. Model. Kokoro / XTTS v2 / F5-TTS / VITS / StyleTTS 2 / commercial API. One-sentence reason.
2. Text frontend. Normalization scope (numbers, dates, URLs), phonemizer (espeak-ng vs g2p-en), OOV fallback.
3. Voice. Preset name or reference clip spec (seconds, noise floor, accent match).
4. Quality targets. Target UTMOS, CER via Whisper, SECS when cloning.
5. Evaluation plan. 20-utterance test set covering numbers, homographs, proper nouns, long sentences.
Refuse any production TTS without a text normalizer. Refuse voice cloning without user consent and watermarking. Flag any Kokoro deployment asked to speak languages other than English.
