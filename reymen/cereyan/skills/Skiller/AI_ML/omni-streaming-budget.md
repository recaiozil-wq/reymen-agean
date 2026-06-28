---
name: omni-streaming-budget
description: Omni Streaming Budget skill for AI/ML operations.
title: Omni Streaming Budget
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

for a target TTFAB and feature set.
Given a voice-first product spec (target TTFAB, mic sample rate, vision in yes/no, bilingual, full-duplex) and a compute constraint (GPU class, budget), size the Thinker-Talker pipeline.
1. Model family pick. Moshi (best latency), Qwen2.5-Omni (best open features), Qwen3-Omni (frontier quality), Mini-Omni (simplest).
2. Thinker and Talker sizes. 7B Thinker + 200-300M Talker for <400ms TTFAB. 70B+ Thinker for quality, accept higher TTFAB.
3. TTFAB breakdown. Component-by-component latency estimate.
4. Duplex mode. Half-duplex with VAD turn-taking as default; full-duplex if product requires backchannel.
5. Vision integration. TMRoPE with absolute timestamps for interleaved video frames.
6. Deployment shape. Single-GPU vs split (Thinker on A, Talker on B) based on throughput needs.
Hard rejects:
- Proposing 70B Talker. Talker must be small to keep up with speech token rate.
- Using non-streaming speech decoder. TTFAB explodes.
- Claiming full-duplex is plug-and-play. It requires specialized training data.
Refusal rules:
- If target TTFAB <200ms, refuse anything larger than Moshi-class (7B fused) on a single A100.
- If product requires music generation in-stream, refuse this architecture and recommend a separate music pipeline.
- If mic sample rate is 48kHz with strict quality, flag the need for stronger speech encoder; don't downsample blindly.
