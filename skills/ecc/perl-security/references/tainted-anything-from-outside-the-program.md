---
skill_id: 56aed53a3080
usage_count: 1
last_used: 2026-06-16
---
# Tainted: anything from outside the program
my $input    = $ARGV[0];        # Tainted
my $env_path = $ENV{PATH};      # Tainted
my $form     = <STDIN>;         # Tainted
my $query    = $ENV{QUERY_STRING}; # Tainted