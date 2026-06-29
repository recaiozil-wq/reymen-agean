---
name: ecc_react-testing_references_tdd-workflow
description: TDD Workflow
title: "Ecc React Testing References Tdd Workflow"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | TDD Workflow |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## TDD Workflow

```
RED     -> Write failing test for the next requirement
GREEN   -> Write minimal component code to pass
REFACTOR -> Improve the component, tests stay green
REPEAT  -> Next requirement
```

For new components:

1. Define the component's prop type and signature
2. Write the first test for the simplest case
3. Verify it fails for the right reason
4. Implement just enough to pass
5. Add the next test case
6. Refactor when the third similar test reveals a pattern
