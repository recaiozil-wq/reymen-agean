---
skill_id: 4e248e7cf836
usage_count: 1
last_used: 2026-06-16
---
## When to use vs alternatives

**Use vLLM when:**
- Deploying production LLM APIs (100+ req/sec)
- Serving OpenAI-compatible endpoints
- Limited GPU memory but need large models
- Multi-user applications (chatbots, assistants)
- Need low latency with high throughput

**Use alternatives instead:**
- **llama.cpp**: CPU/edge inference, single-user
- **HuggingFace transformers**: Research, prototyping, one-off generation
- **TensorRT-LLM**: NVIDIA-only, need absolute maximum performance
- **Text-Generation-Inference**: Already in HuggingFace ecosystem