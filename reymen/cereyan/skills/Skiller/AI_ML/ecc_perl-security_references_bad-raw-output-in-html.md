---
name: ecc_perl-security_references_bad-raw-output-in-html
description: "Bad: Raw output in HTML"
title: "Ecc Perl Security References Bad Raw Output In Html"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Raw output in HTML |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Raw output in HTML
sub bad_html($input) {
    print "<div>$input</div>";  # XSS if $input contains <script>
}
```

### CSRF Protection

```perl
use v5.36;
use Crypt::URandom qw(urandom);
use MIME::Base64 qw(encode_base64url);

sub generate_csrf_token() {
    return encode_base64url(urandom(32));
}
```

Use constant-time comparison when verifying tokens. Most web frameworks (Mojolicious, Dancer2, Catalyst) provide built-in CSRF protection — prefer those over hand-rolled solutions.

### Session and Header Security

```perl
use v5.36;
