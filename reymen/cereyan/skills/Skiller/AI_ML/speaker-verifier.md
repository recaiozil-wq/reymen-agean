---
name: speaker-verifier
description: Speaker Verifier skill for AI/ML operations.
title: Speaker Verifier
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

enrollment protocol, and threshold tuning.
Given a target (verification vs identification vs diarization, domain, channel, threat model) and data (hours for threshold tuning, number of speakers, enrollment clip budget), output:
1. Embedder. ECAPA-TDNN / WavLM-SV / ReDimNet / x-vector. Reason.
2. Enrollment protocol. Number of clips, min duration, noise gate, channel match.
3. Scoring. Cosine / PLDA; with or without AS-norm; cohort size.
4. Threshold. Target FAR (fraud risk) or EER; tuning set size.
5. Spoof defense. Anti-spoof model (AASIST, RawNet2), liveness challenge, or replay detection.
Refuse any fraud-grade deployment without an anti-spoof front-end. Refuse to publish EER without reporting the evaluation set, its channel, and clip length distribution. Flag cosine thresholds fixed across domains without re-tuning.
