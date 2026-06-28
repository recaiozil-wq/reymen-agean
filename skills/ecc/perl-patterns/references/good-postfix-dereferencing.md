---
skill_id: 0c90b7605ce0
usage_count: 1
last_used: 2026-06-16
---
# Good: Postfix dereferencing
my @users = $data->{users}->@*;
my @roles = $data->{users}[0]{roles}->@*;
my %first = $data->{users}[0]->%*;