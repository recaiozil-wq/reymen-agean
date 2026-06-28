---
name: software-development_node-inspect-debugger_references_run-a-single-test-file-paused-on-entry
description: Run a single test file paused on entry
title: "Software Development Node Inspect Debugger References Run A Single Test File Paused On Entry"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Run a single test file paused on entry |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Run a single test file paused on entry
node --inspect-brk ./node_modules/vitest/vitest.mjs run --no-file-parallelism src/app/foo.test.tsx
```

In another terminal: `node inspect -p <pid>`, then `sb('src/app/foo.tsx', 42)`, `cont`.

Use `--no-file-parallelism` (vitest) or `--runInBand` (jest) so only one worker exists — debugging a pool is painful.
