---
skill_id: 398da173ce82
usage_count: 1
last_used: 2026-06-16
---
## Data Classes and Named Tuples

### Data Classes

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    """User entity with automatic __init__, __repr__, and __eq__."""
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True