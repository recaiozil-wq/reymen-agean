---
skill_id: 49ed616b4ff3
usage_count: 1
last_used: 2026-06-16
---
# Verify call count
    my $call_count = 0;
    $mock->mock(fetch_user => sub { $call_count++; return {} });
    $api->fetch_user(1);
    $api->fetch_user(2);
    is($call_count, 2, 'fetch_user called twice');