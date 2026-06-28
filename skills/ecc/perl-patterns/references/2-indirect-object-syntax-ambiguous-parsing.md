---
skill_id: 30ce2c43a9d0
usage_count: 1
last_used: 2026-06-16
---
# 2. Indirect object syntax (ambiguous parsing)
my $obj = new Foo(bar => 1);            # Bad
my $obj = Foo->new(bar => 1);           # Good