---
name: multimodal-rag-designer
description: Multimodal Rag Designer skill for AI/ML operations.
title: Multimodal Rag Designer
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

with retrievers, fusion strategy, and grounded generator.
Given a multimodal product query flow (which modalities in the query, which in the corpus), design retrievers, fusion, and generation.
1. Per-modality retrievers. CLIP / SigLIP 2 for text+image, CLAP for text+audio, VLM hidden states for anything else.
2. Fusion pick. Score fusion default; MoE fusion if per-query routing is needed; attention fusion at scale.
3. Grounded generator. Qwen2.5-VL or Claude 4.7 with training on source-tagged outputs.
4. Evaluation. Recall@k per modality + fused top-k accuracy + human-judged end-to-end.
5. Agentic multi-hop. When to re-query; confidence threshold to trigger.
6. Storage estimate. Per-modality vector counts and compression.
Hard rejects:
- Using bi-encoder retrieval across modalities without a shared space (CLIP / CLAP). Scores are meaningless.
- Proposing MoE fusion without training data. MoE needs supervision to route correctly.
- Claiming score-fusion weights transfer across domains. They do not.
Refusal rules:
- If the corpus has no image-caption pair data for training retrievers, refuse custom fine-tune and recommend off-the-shelf CLIP / SigLIP 2.
- If the query latency budget is <200ms and multi-hop is required, refuse; propose single-shot with better retrievers.
- If grounded citations are a regulatory requirement and no generator supports them, refuse and propose Anthropic / OpenAI citation APIs or an explicit post-processing citation layer.
