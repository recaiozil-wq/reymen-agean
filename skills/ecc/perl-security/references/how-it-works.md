---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

Start with taint-aware input boundaries, then move outward: validate and untaint inputs, keep filesystem and process execution constrained, and use parameterized DBI queries everywhere. The examples below show the safe defaults this skill expects you to apply before shipping Perl code that touches user input, the shell, or the network.