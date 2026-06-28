---
name: software-development_node-inspect-debugger_references_4-attach
description: 4.
title: "Software Development Node Inspect Debugger References 4 Attach"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 4.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# 4. Attach
node inspect ws://127.0.0.1:9229/<uuid>
```

Interacting with the TUI (typing in its window) continues to advance execution; your debugger can pause it on a breakpoint at any `sb(...)`.

### Debugging `_SlashWorker` / PTY child processes

Those are Python, not Node — use the `python-debugpy` skill for them. Only Node portions (Ink UI, tui_gateway client, tsx-run tests under `ui-tui/`) use this skill.
