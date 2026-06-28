---
name: finetuning-pipeline
description: Finetuning Pipeline skill for AI/ML operations.
title: Finetuning Pipeline
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

ablations, quantization, and a 2026 Model Openness Framework model card.
Given a base model (Llama 3.3 8B, Qwen3 14B, or Gemma 3 12B) and a task-specific dataset, build a single-command pipeline that produces a served endpoint and a reproducible model card.
Build plan:
1. Data stage: Datatrove dedup, Nemotron-CC-style quality filter, Presidio PII scrub, seeded train/val splits.
2. Contamination check: MinHashLSH against MMLU-Pro, MT-Bench-v2, RewardBench-2. Reject on overlap.
3. SFT: Axolotl v0.8 with ZeRO-3, Flash Attention 3, packed sequences, 2-3 epochs on 8xH100.
4. Preference tuning: TRL 0.15 DPO (or GRPO with verifiable rewards) for 1 epoch, beta sweep.
5. Quantize: GPTQ-INT4-Marlin + AWQ-INT4 + GGUF-Q4_K_M.
6. Serve: vLLM 0.7 with EAGLE-3 speculative decoding (draft heads via Red Hat Speculators or SGLang SpecForge). K8s deployment with HPA on queue-wait.
7. Eval: lm-evaluation-harness, RewardBench-2, MT-Bench-v2, MMLU-Pro across base/SFT-only/SFT+DPO/SFT+GRPO.
8. Safety: Llama Guard 4 pass rate, ShieldGemma-2 output filter.
9. Model card under 2026 Model Openness Framework with data, training, eval, safety, reproducibility sections.
Assessment rubric:
Hard rejects:
- Pipelines that skip the MinHash contamination check. Leaking MMLU-Pro into training is the classic eval-cheating failure mode.
- Training runs without seeds or YAMLs attached. Reproducibility is a hard requirement.
- Serving without EAGLE-3 or an equivalent speculative decoding configuration. Baseline tokens/s is not the 2026 bar.
- Missing safety eval. Every fine-tune ships with a Llama Guard 4 pass rate.
Refusal rules:
- Refuse to publish a model card that claims benchmark scores without attaching the lm-eval-harness commit SHA.
- Refuse to fine-tune on data whose license forbids derivative models. MOF grades data licensing.
- Refuse to ship a quantized model without measuring quality loss on the eval matrix.
