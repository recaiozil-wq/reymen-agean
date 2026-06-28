---
skill_id: 7f81bedf2813
usage_count: 1
last_used: 2026-06-16
---
# Skip tests conditionally
SKIP: {
    skip 'No database configured', 2 unless $ENV{TEST_DB};

    my $db = connect_db();
    ok($db->ping, 'database is reachable');
    is($db->version, '15', 'correct PostgreSQL version');
}