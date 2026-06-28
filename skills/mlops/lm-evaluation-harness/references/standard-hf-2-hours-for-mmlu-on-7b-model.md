---
skill_id: 827a0ee2be68
usage_count: 1
last_used: 2026-06-16
---
# Standard HF: ~2 hours for MMLU on 7B model
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --batch_size 8