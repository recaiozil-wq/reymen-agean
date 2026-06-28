---
skill_id: 45ea36ae12b8
usage_count: 1
last_used: 2026-06-16
---
# Hash builder — check partial structure
is(
    $user->to_hash,
    hash {
        field name  => 'Alice';
        field email => match(qr/\@example\.com$/);
        field age   => validator(sub { $_ >= 18 });