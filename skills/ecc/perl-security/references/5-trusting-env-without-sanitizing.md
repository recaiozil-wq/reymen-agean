---
skill_id: 68c08e406bee
usage_count: 1
last_used: 2026-06-16
---
# 5. Trusting $ENV without sanitizing
my $path = $ENV{UPLOAD_DIR};             # Could be manipulated
system("ls $path");                      # Double vulnerability