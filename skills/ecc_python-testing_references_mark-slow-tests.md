---
name: ecc_python-testing_references_mark-slow-tests
description: Mark slow tests
title: "Ecc Python Testing References Mark Slow Tests"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Mark slow tests |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Mark slow tests
@pytest.mark.slow
def test_slow_operation():
    time.sleep(5)
