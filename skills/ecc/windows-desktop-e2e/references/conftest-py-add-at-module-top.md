---
skill_id: 1d68de35b46a
usage_count: 1
last_used: 2026-06-16
---
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