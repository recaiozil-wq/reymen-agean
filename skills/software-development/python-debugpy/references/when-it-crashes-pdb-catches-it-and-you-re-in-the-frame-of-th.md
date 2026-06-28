---
skill_id: e46c03fa5e51
usage_count: 1
last_used: 2026-06-16
---
# When it crashes, pdb catches it and you're in the frame of the exception
```

Or set a global hook in a repl/jupyter:

```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```