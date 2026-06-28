---
name: ecc_windows-desktop-e2e_references_locators-priority-order
description: --- Locators (priority order) ---
title: "Ecc Windows Desktop E2E References Locators Priority Order"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | --- Locators (priority order) --- |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# --- Locators (priority order) ---

    def by_id(self, auto_id, **kw):
        """AutomationId — most stable. Use as first choice."""
        return self.window.child_window(auto_id=auto_id, **kw)

    def by_name(self, name, **kw):
        """Visible text / accessible name."""
        return self.window.child_window(title=name, **kw)

    def by_class(self, cls, index=0, **kw):
        """Control class + index — fragile, avoid if possible."""
        return self.window.child_window(class_name=cls, found_index=index, **kw)
