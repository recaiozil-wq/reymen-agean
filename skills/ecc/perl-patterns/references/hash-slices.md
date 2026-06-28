---
skill_id: e6ba05b774d9
usage_count: 1
last_used: 2026-06-16
---
# Hash slices
my %subset;
@subset{qw(host port)} = @{$config->{database}}{qw(host port)};