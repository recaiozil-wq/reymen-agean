---
name: ecc_windows-desktop-e2e_references_wait-for-control-to-disappear-e-g-loading-spinner
description: Wait for control to disappear (e.g.
title: "Ecc Windows Desktop E2E References Wait For Control To Disappear E G Loading Spinner"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Wait for control to disappear (e.g. |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Wait for control to disappear (e.g. loading spinner)
page.wait_gone(page.by_id("spinnerOverlay"))
