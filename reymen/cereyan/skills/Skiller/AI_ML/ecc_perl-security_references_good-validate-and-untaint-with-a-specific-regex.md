---
name: ecc_perl-security_references_good-validate-and-untaint-with-a-specific-regex
description: "Good: Validate and untaint with a specific regex"
title: "Ecc Perl Security References Good Validate And Untaint With A Specific Regex"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Good: Validate and untaint with a specific regex |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Good: Validate and untaint with a specific regex
sub untaint_username($input) {
    if ($input =~ /^([a-zA-Z0-9_]{3,30})$/) {
        return $1;  # $1 is untainted
    }
    die "Invalid username: must be 3-30 alphanumeric characters\n";
}
