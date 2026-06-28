---
name: ecc_windows-desktop-e2e_references_per-step-trace-opt-in
description: Per-Step Trace (opt-in)
title: "Ecc Windows Desktop E2E References Per Step Trace Opt In"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Per-Step Trace (opt-in) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Per-Step Trace (opt-in)

The default failure screenshot is often too thin for diagnosing flaky tests. The step-level trace below is **off by default** — enable it only when reproducing a flaky case.

### Enable

```bash
E2E_TRACE=1 pytest tests/test_login.py -v
