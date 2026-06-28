---
name: software-development_python-debugpy_references_debugpy-injects-itself-into-the-process-then-attach-a-client
description: debugpy injects itself into the process.
title: "Software Development Python Debugpy References Debugpy Injects Itself Into The Process Then Attach A Client"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | debugpy injects itself into the process. |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# debugpy injects itself into the process. Then attach a client as below.
```

Some kernels/security configs block the ptrace-based injection (`/proc/sys/kernel/yama/ptrace_scope`). Fix with:
```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

### Connecting a client from the terminal

The easiest terminal-side DAP client is VS Code CLI or a small script. From inside Hermes you have two practical options:

**Option 1: `debugpy`'s own CLI REPL** — not an official feature, but a tiny DAP client script:

```python
