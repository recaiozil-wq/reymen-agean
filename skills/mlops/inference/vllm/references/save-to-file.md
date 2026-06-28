---
skill_id: 8c949fa720b8
usage_count: 1
last_used: 2026-06-16
---
# Save to file
import json
with open("results.jsonl", "w") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(f"Processed {len(results)} prompts")
```

### Workflow 3: Quantized model serving

Fit large models in limited GPU memory.

```
Quantization Setup:
- [ ] Step 1: Choose quantization method
- [ ] Step 2: Find or create quantized model
- [ ] Step 3: Launch with quantization flag
- [ ] Step 4: Verify accuracy
```

**Step 1: Choose quantization method**

- **AWQ**: Best for 70B models, minimal accuracy loss
- **GPTQ**: Wide model support, good compression
- **FP8**: Fastest on H100 GPUs

**Step 2: Find or create quantized model**

Use pre-quantized models from HuggingFace:

```bash