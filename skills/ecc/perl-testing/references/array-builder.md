---
skill_id: 126665e4155e
usage_count: 1
last_used: 2026-06-16
---
# Array builder
is(
    $result,
    array {
        item 'first';
        item match(qr/^second/);
        item DNE();  # Does Not Exist — verify no extra items
    },
    'result matches expected list'
);