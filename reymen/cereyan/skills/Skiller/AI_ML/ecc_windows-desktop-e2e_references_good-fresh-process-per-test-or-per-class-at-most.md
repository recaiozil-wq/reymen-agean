---
name: ecc_windows-desktop-e2e_references_good-fresh-process-per-test-or-per-class-at-most
description: "GOOD: fresh process per test (or per class at most)"
title: "Ecc Windows Desktop E2E References Good Fresh Process Per Test Or Per Class At Most"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | GOOD: fresh process per test (or per class at most) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# GOOD: fresh process per test (or per class at most)
@pytest.fixture(scope="function")
def app(): ...
```
