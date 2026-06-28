---
name: ecc_react-testing_references_when-not-to-use-snapshot-tests
description: When NOT to Use Snapshot Tests
title: "Ecc React Testing References When Not To Use Snapshot Tests"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | When NOT to Use Snapshot Tests |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## When NOT to Use Snapshot Tests

Snapshots of rendered output:

- Break on every styling change
- Get rubber-stamped during review
- Test implementation detail (DOM structure), not behavior

Acceptable snapshot uses:

- Pure data serialization functions (`formatInvoice(invoice)` -> stable string)
- Generated config files (e.g., webpack config output)

For visual regression on components, use Playwright/Cypress screenshots or Percy/Chromatic — actual visual diffs, not DOM strings.
