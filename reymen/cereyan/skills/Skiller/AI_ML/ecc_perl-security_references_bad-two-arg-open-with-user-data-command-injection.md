---
name: ecc_perl-security_references_bad-two-arg-open-with-user-data-command-injection
description: "Bad: Two-arg open with user data (command injection)"
title: "Ecc Perl Security References Bad Two Arg Open With User Data Command Injection"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Two-arg open with user data (command injection) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Two-arg open with user data (command injection)
sub bad_read($path) {
    open my $fh, $path;        # If $path = "|rm -rf /", runs command!
    open my $fh, "< $path";   # Shell metacharacter injection
}
```

### TOCTOU Prevention and Path Traversal

```perl
use v5.36;
use Fcntl qw(:DEFAULT :flock);
use File::Spec;
use Cwd qw(realpath);
