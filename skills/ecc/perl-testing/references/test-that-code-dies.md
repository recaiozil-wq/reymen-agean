---
skill_id: f0902be81109
usage_count: 1
last_used: 2026-06-16
---
# Test that code dies
like(
    dies { divide(10, 0) },
    qr/Division by zero/,
    'dies on division by zero'
);