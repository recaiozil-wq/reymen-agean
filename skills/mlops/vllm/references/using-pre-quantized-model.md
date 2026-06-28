---
skill_id: 8ddd7feac91d
usage_count: 1
last_used: 2026-06-16
---
# Using pre-quantized model
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95