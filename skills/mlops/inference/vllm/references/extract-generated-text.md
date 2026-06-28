---
skill_id: 0cd0118b3e31
usage_count: 1
last_used: 2026-06-16
---
# Extract generated text
results = []
for output in outputs:
    prompt = output.prompt
    generated = output.outputs[0].text
    results.append({
        "prompt": prompt,
        "generated": generated,
        "tokens": len(output.outputs[0].token_ids)
    })