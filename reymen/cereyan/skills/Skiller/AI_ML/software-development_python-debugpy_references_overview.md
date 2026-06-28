---
name: software-development_python-debugpy_references_overview
description: Overview
title: "Software Development Python Debugpy References Overview"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Overview |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Overview

Three tools, picked by situation:

| Tool | When |
|---|---|
| **`breakpoint()` + pdb** | Local, interactive, simplest. Add `breakpoint()` in the source, run normally, get a REPL at that line. |
| **`python -m pdb`** | Launch an existing script under pdb with no source edits. Useful for quick poking. |
| **`debugpy`** | Remote / headless / "attach to already-running process." Talks DAP, scriptable from terminal, works for long-lived processes (gateway, daemon, PTY children). |

**Start with `breakpoint()`.** It's the cheapest thing that works.
