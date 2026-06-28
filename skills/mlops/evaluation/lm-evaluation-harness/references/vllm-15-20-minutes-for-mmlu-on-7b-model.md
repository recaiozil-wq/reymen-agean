---
skill_id: 4a2f7e81850d
usage_count: 1
last_used: 2026-06-16
---
# vLLM: ~15-20 minutes for MMLU on 7B model
lm_eval --model vllm \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,tensor_parallel_size=2 \
  --tasks mmlu \
  --batch_size auto
```