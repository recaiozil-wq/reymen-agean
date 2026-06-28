---
skill_id: def1e9097b4f
usage_count: 1
last_used: 2026-06-16
---
# The generator runs as normal
output = generate(task_spec)
```

### Phase 2: Check It Twice (Independent Dual Review)

Spawn two review agents in parallel. Critical invariants:

1. **Context isolation** — neither reviewer sees the other's assessment
2. **Identical rubric** — both receive the same evaluation criteria
3. **Same inputs** — both receive the original spec AND the generated output
4. **Structured output** — each returns a typed verdict, not prose

```python
REVIEWER_PROMPT = """
You are an independent quality reviewer. You have NOT seen any other review of this output.