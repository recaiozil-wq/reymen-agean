---
name: ecc_perl-security_references_bad-directly-interpolating-user-chosen-column
description: "Bad: Directly interpolating user-chosen column"
title: "Ecc Perl Security References Bad Directly Interpolating User Chosen Column"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Directly interpolating user-chosen column |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Directly interpolating user-chosen column
sub bad_order($dbh, $column) {
    $dbh->prepare("SELECT * FROM users ORDER BY $column");  # SQLi!
}
```

### DBIx::Class (ORM Safety)

```perl
use v5.36;
