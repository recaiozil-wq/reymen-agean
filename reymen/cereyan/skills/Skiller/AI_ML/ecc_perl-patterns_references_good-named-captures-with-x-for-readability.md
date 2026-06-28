---
name: ecc_perl-patterns_references_good-named-captures-with-x-for-readability
description: "Good: Named captures with /x for readability"
title: "Ecc Perl Patterns References Good Named Captures With X For Readability"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_good-named-captures-with-x-for-readability.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Good: Named captures with /x for readability
my $log_re = qr{
    ^ (?<timestamp> \d{4}-\d{2}-\d{2} \s \d{2}:\d{2}:\d{2} )
    \s+ \[ (?<level> \w+ ) \]
    \s+ (?<message> .+ ) $
}x;

if ($line =~ $log_re) {
    say "Time: $+{timestamp}, Level: $+{level}";
    say "Message: $+{message}";
}
