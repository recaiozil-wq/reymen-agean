---
skill_id: 37e4831f66d9
usage_count: 1
last_used: 2026-06-16
---
# For 30B-70B models with tensor parallelism
vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.9 \
  --quantization awq \
  --port 8000