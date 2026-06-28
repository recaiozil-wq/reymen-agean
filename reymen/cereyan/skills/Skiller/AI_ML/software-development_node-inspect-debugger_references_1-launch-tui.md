---
name: software-development_node-inspect-debugger_references_1-launch-tui
description: 1.
title: "Software Development Node Inspect Debugger References 1 Launch Tui"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 1.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# 1. Launch TUI
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)
