---
name: ecc_windows-desktop-e2e_references_qt-specific
description: Qt Specific
title: "Ecc Windows Desktop E2E References Qt Specific"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Qt Specific |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Qt Specific

### Enable UIA in Qt 5.x

Qt 5.x accessibility is disabled by default in some builds (especially 5.7–5.14). Set the environment variable **before** launching. Qt 6.x enables accessibility by default — skip this step for Qt 6.

```python
