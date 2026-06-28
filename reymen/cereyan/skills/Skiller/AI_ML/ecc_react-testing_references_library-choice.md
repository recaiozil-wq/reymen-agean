---
name: ecc_react-testing_references_library-choice
description: Library Choice
title: "Ecc React Testing References Library Choice"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Library Choice |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Library Choice

| Runner | When | Note |
|---|---|---|
| **Vitest** | Vite, Remix, modern setups | Faster, native ESM, Jest-compatible API |
| **Jest** | Next.js, CRA, established repos | Default for many React projects |
| **Playwright Component Testing** | Real browser engine needed | Use when JSDOM lacks the required feature |
| **Cypress Component Testing** | Real browser, Cypress already in use | Alternative to Playwright CT |

Pick one. Do not run RTL + Vitest AND Playwright CT in the same repo unless you have a clear lane separation.
