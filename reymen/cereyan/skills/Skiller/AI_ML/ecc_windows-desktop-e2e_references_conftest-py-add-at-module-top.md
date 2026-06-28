---
name: ecc_windows-desktop-e2e_references_conftest-py-add-at-module-top
description: conftest.py — add at module top
title: "Ecc Windows Desktop E2E References Conftest Py Add At Module Top"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | conftest.py — add at module top |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# conftest.py — add at module top
import os
os.environ["QT_ACCESSIBILITY"] = "1"
```

Or export it in CI:

```yaml
env:
  QT_ACCESSIBILITY: "1"
```

### Add Stable Identifiers to Qt Widgets

```cpp
// Preferred: both objectName and accessibleName
void setTestId(QWidget* w, const char* id) {
    w->setObjectName(id);
    w->setAccessibleName(id);  // becomes UIA Name property
}

// In your dialog constructor:
setTestId(ui->usernameEdit, "usernameInput");
setTestId(ui->passwordEdit, "passwordInput");
setTestId(ui->loginButton,  "btnLogin");
setTestId(ui->errorLabel,   "lblError");
```

Centralise all IDs in a header to avoid typos:

```cpp
// test_ids.h
#define TID_USERNAME   "usernameInput"
#define TID_PASSWORD   "passwordInput"
#define TID_BTN_LOGIN  "btnLogin"
#define TID_LBL_ERROR  "lblError"
```

### Qt-Specific Quirks

**QComboBox** — the dropdown is a separate top-level window:

```python
from pywinauto import Desktop

def select_combo_item(page, combo_spec, item_text):
    page.click(combo_spec)
