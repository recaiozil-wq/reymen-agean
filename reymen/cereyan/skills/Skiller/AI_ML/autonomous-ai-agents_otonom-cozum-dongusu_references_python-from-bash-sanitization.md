---
name: autonomous-ai-agents_otonom-cozum-dongusu_references_python-from-bash-sanitization
description: Python-from-Bash sanitization on Windows (relevant to this class)
title: "Autonomous Ai Agents Otonom Cozum Dongusu References Python From Bash Sanitization"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Python-from-Bash sanitization on Windows (relevant to this class) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Python-from-Bash sanitization on Windows (relevant to this class)

## Problem
Running inline Python from bash on Windows mangles quotes, backslashes, and Unicode codepoints, so the executing shell sees broken input and the script fails or produces garbled output.

## Fix
Always write the script to a temp file, then execute it by path:

```bash
python - << 'PY'
# ... multi-line Python ...
PY
```

## When this applies
- Any `terminal` call that invokes Python with embedded quotes, paths with backslashes, or Turkish characters.
- Any shell snippet that builds a command string dynamically and then executes it.
- Any `.env` update via shell: prefer Python file-write instead of bash echo.

## Rationale
Bash does the expansion and quoting; Python just reads the file. No escape-layer, no character loss.
