---
name: ecc_perl-testing_references_quick-reference
description: Quick Reference
title: "Ecc Perl Testing References Quick Reference"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Quick Reference |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Quick Reference

| Task | Command / Pattern |
|---|---|
| Run all tests | `prove -lr t/` |
| Run one test verbose | `prove -lv t/unit/user.t` |
| Parallel test run | `prove -lr -j8 t/` |
| Coverage report | `cover -test && cover -report html` |
| Test equality | `is($got, $expected, 'label')` |
| Deep comparison | `is($got, hash { field k => 'v'; etc() }, 'label')` |
| Test exception | `like(dies { ... }, qr/msg/, 'label')` |
| Test no exception | `ok(lives { ... }, 'label')` |
| Mock a method | `Test::MockModule->new('Pkg')->mock(m => sub { ... })` |
| Skip tests | `SKIP: { skip 'reason', $count unless $cond; ... }` |
| TODO tests | `TODO: { local $TODO = 'reason'; ... }` |
