---
name: ecc_windows-desktop-e2e_references_skip-in-ci-only
description: Skip in CI only
title: "Ecc Windows Desktop E2E References Skip In Ci Only"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Skip in CI only |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Skip in CI only
@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Flaky in CI #43")
def test_heavy_load(self, app): ...
```

Common causes and fixes:

| Cause | Fix |
|-------|-----|
| Control not ready | Replace `time.sleep` with `wait_visible` |
| Window not focused | Add `win.set_focus()` before interactions |
| Animation in progress | `wait_until(lambda: not loading_indicator.exists())` |
| Dialog timing | `wait_window(title, timeout=15)` |
| CI display not ready | Set `DISPLAY` or use virtual desktop in CI |
| `set_edit_text` raises NotImplementedError | UIA ValuePattern missing (common on Qt 5.x) — `BasePage.type_text` already falls back to `keyboard.send_keys` |
| Control exists but `wait_visible` times out | Window minimised or off-screen — call `win.restore()` + `win.set_focus()` before waiting |
