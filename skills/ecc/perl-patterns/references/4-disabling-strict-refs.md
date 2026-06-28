---
skill_id: ad15c3480b6d
usage_count: 1
last_used: 2026-06-16
---
# 4. Disabling strict refs
no strict 'refs';                        # Almost always wrong
${"My::Package::$var"} = $value;         # Use a hash instead