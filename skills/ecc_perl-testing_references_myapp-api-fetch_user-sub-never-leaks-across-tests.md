---
name: ecc_perl-testing_references_myapp-api-fetch_user-sub-never-leaks-across-tests
description: "*MyApp::API::fetch_user = sub { ..."
title: "Ecc Perl Testing References Myapp Api Fetch User Sub Never Leaks Across Tests"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | *MyApp::API::fetch_user = sub { ... |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# *MyApp::API::fetch_user = sub { ... };  # NEVER — leaks across tests
```

For lightweight mock objects, use `Test::MockObject` to create injectable test doubles with `->mock()` and verify calls with `->called_ok()`.
