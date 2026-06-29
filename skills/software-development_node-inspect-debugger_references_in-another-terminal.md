---
name: software-development_node-inspect-debugger_references_in-another-terminal
description: "In another terminal:"
title: "Software Development Node Inspect Debugger References In Another Terminal"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | In another terminal: |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# In another terminal:
node inspect -p <node pid>
```

Then inside `debug>`:

```
sb('dist/app.js', 220)     # or wherever the suspect render is
cont
```

When it pauses, `repl` → inspect `props`, state refs, `useInput` handler values, etc.

### Debugging a running `hermes --tui`

The TUI spawns Node from the Python CLI. Easiest path:

```bash
