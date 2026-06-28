---
skill_id: 55173e2aa8aa
usage_count: 1
last_used: 2026-06-16
---
# Python 3.8 and earlier - Use typing module
from typing import List, Dict

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

### Type Aliases and TypeVar

```python
from typing import TypeVar, Union