---
name: ecc_windows-desktop-e2e_references_bad-share-app-instance-across-all-tests-state-leaks
description: "BAD: share app instance across all tests (state leaks)"
title: "Ecc Windows Desktop E2E References Bad Share App Instance Across All Tests State Leaks"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | BAD: share app instance across all tests (state leaks) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# BAD: share app instance across all tests (state leaks)
@pytest.fixture(scope="session")
def app(): ...
