---
name: ecc_santa-method_references_pseudocode-for-agent-tool-invocation
description: Pseudocode for Agent tool invocation
title: "Ecc Santa Method References Pseudocode For Agent Tool Invocation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Pseudocode for Agent tool invocation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Pseudocode for Agent tool invocation
reviewer_b = Agent(
    description="Santa Review B",
    prompt=f"Review this output for quality...\n\nRUBRIC:\n{rubric}\n\nOUTPUT:\n{output}"
)
reviewer_c = Agent(
    description="Santa Review C",
    prompt=f"Review this output for quality...\n\nRUBRIC:\n{rubric}\n\nOUTPUT:\n{output}"
)
```

### Pattern B: Sequential Inline (Fallback)

When subagents aren't available, simulate isolation with explicit context resets:

1. Generate output
2. New context: "You are Reviewer 1. Evaluate ONLY against this rubric. Find problems."
3. Record findings verbatim
4. Clear context completely
5. New context: "You are Reviewer 2. Evaluate ONLY against this rubric. Find problems."
6. Compare both reviews, fix, repeat

The subagent pattern is strictly superior — inline simulation risks context bleed between reviewers.

### Pattern C: Batch Sampling

For large batches (100+ items), full Santa on every item is cost-prohibitive. Use stratified sampling:

1. Run Santa on a random sample (10-15% of batch, minimum 5 items)
2. Categorize failures by type (hallucination, compliance, completeness, etc.)
3. If systematic patterns emerge, apply targeted fixes to the entire batch
4. Re-sample and re-verify the fixed batch
5. Continue until a clean sample passes

```python
import random

def santa_batch(items, rubric, sample_rate=0.15):
    sample = random.sample(items, max(5, int(len(items) * sample_rate)))

    for item in sample:
        result = santa_full(item, rubric)
        if result.verdict == "NAUGHTY":
            pattern = classify_failure(result.issues)
            items = batch_fix(items, pattern)  # Fix all items matching pattern
            return santa_batch(items, rubric)   # Re-sample

    return items  # Clean sample → ship batch
```
