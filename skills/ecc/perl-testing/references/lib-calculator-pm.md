---
skill_id: f073e57f4560
usage_count: 1
last_used: 2026-06-16
---
# lib/Calculator.pm
package Calculator;
use v5.36;
use Moo;

sub add($self, $a, $b) {
    return $a + $b;
}

1;