---
name: ecc_react-testing_references_core-principle
description: Core Principle
title: "Ecc React Testing References Core Principle"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Core Principle |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Core Principle

Test what the user sees and does, not implementation details.

A test should:

- Render the component with the same providers it has in production
- Interact with it via accessible queries (role, label) and `userEvent`
- Assert visible output and observable side effects (callback fired, request sent)

A test should NOT:

- Inspect component state, props passed to children, or which hooks were called
- Mock React itself or framework hooks
- Assert on the number of renders or DOM structure beyond what affects users
