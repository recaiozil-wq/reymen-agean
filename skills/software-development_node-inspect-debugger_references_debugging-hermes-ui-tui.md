---
name: software-development_node-inspect-debugger_references_debugging-hermes-ui-tui
description: Debugging Hermes ui-tui
title: "Software Development Node Inspect Debugger References Debugging Hermes Ui Tui"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Debugging Hermes ui-tui |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Debugging Hermes ui-tui

The TUI is built Ink + tsx. Two common scenarios:

### Debugging a single Ink component under dev

`ui-tui/package.json` has `npm run dev` (tsx --watch). Add `--inspect-brk` by running tsx directly:

```bash
cd /home/bb/hermes-agent/ui-tui
npm run build    # produce dist/ once so transpile isn't needed on first load
node --inspect-brk dist/entry.js
