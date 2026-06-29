---
name: ecc_windows-desktop-e2e_references_bad-brittle-class-index-locator-as-primary-strategy
description: "BAD: brittle class+index locator as primary strategy"
title: "Ecc Windows Desktop E2E References Bad Brittle Class Index Locator As Primary Strategy"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | BAD: brittle class+index locator as primary strategy |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# BAD: brittle class+index locator as primary strategy
page.by_class("Edit", index=2).type_keys("hello")
