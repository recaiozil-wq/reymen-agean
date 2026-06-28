---
name: ecc_windows-desktop-e2e_references_page-object-model
description: Page Object Model
title: "Ecc Windows Desktop E2E References Page Object Model"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Page Object Model |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
