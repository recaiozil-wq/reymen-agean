---
skill_id: 88a98bfb3ab4
usage_count: 1
last_used: 2026-06-16
---
# Good: Yields lines one at a time
def read_lines(path: str) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            yield line.strip()
```

### Avoid String Concatenation in Loops

```python