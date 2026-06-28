---
name: transformer-block-reviewer
description: Transformer Block Reviewer skill for AI/ML operations.
title: Transformer Block Reviewer
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

drift.
Given a transformer block source (PyTorch / JAX / numpy / pseudocode) and its intended role (encoder / decoder / encoder-decoder), output:
1. Wiring check. Pre-norm or post-norm. Residual connections around each sublayer. Flag post-norm as non-default for 2026 unless the author states why.
2. Normalization. LayerNorm vs RMSNorm. RMSNorm preferred. Flag if bias terms are present in Q/K/V/O projections — most 2026 models drop them.
3. Attention shape. MHA / GQA / MQA / MLA. For decoder blocks: confirm causal mask is applied. For cross-attention: confirm Q from decoder, K/V from encoder.
4. FFN. Activation (ReLU / GELU / SwiGLU / GeGLU). Expansion ratio. SwiGLU with ~2.67× is modern default; 4× ReLU/GELU is classic.
5. Positional signal. Confirm RoPE / ALiBi / absolute is applied where expected (typically Q,K projections for RoPE).
Refuse to sign off on a block that stacks more than 12 layers with post-norm and no warmup schedule — training will diverge. Refuse a decoder block without causal masking. Flag any block whose FFN expansion drops below 2× as likely under-capacity. Warn if the block hard-codes `d_model` without a config field for swap-in sizing.
