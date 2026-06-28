---
name: ecc_perl-security_references_bad-string-form-shell-injection
description: "Bad: String form — shell injection!"
title: "Ecc Perl Security References Bad String Form Shell Injection"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: String form — shell injection! |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: String form — shell injection!
sub bad_search($pattern) {
    system("grep -r '$pattern' /var/log/app/");  # If $pattern = "'; rm -rf / #"
}
