---
skill_id: ef644969af51
usage_count: 1
last_used: 2026-06-16
---
# For 7B-13B models on single GPU
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --port 8000