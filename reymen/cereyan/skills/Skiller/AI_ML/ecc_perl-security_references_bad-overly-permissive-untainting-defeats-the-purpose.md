---
name: ecc_perl-security_references_bad-overly-permissive-untainting-defeats-the-purpose
description: "Bad: Overly permissive untainting (defeats the purpose)"
title: "Ecc Perl Security References Bad Overly Permissive Untainting Defeats The Purpose"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Overly permissive untainting (defeats the purpose) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Overly permissive untainting (defeats the purpose)
sub bad_untaint($input) {
    $input =~ /^(.*)$/s;
    return $1;  # Accepts ANYTHING — pointless
}
```
