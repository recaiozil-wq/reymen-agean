---
name: red-teaming_godmode_references_in-execute_code-use-the-loader-to-avoid-exec-scoping-issues
description: "In execute_code — use the loader to avoid exec-scoping issues:"
title: "Red Teaming Godmode References In Execute Code Use The Loader To Avoid Exec Scoping Issues"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | In execute_code — use the loader to avoid exec-scoping issues: |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# In execute_code — use the loader to avoid exec-scoping issues:
import os
exec(open(os.path.expanduser(
    os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), "skills/red-teaming/godmode/scripts/load_godmode.py")
)).read())
