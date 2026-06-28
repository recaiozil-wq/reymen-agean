---
skill_id: c3d05d122cf2
usage_count: 1
last_used: 2026-06-16
---
## Page Object Model

```
tests/
├── conftest.py          # app launch fixture, failure screenshot
├── pytest.ini
├── config.py
├── pages/
│   ├── __init__.py      # required for imports
│   ├── base_page.py     # locators, wait, screenshot helpers
│   ├── login_page.py
│   └── main_page.py
├── tests/
│   ├── __init__.py
│   ├── test_login.py
│   └── test_main_flow.py
└── artifacts/           # screenshots, videos, logs
```

### base_page.py

```python
import os, time
from pywinauto import Desktop
from config import ACTION_TIMEOUT, ARTIFACT_DIR

class BasePage:
    def __init__(self, window):
        self.window = window