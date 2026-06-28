---
skill_id: d54b05451ecb
usage_count: 1
last_used: 2026-06-16
---
# $host is required, others have defaults
    return DBI->connect("dbi:Pg:host=$host;port=$port", undef, undef, {
        RaiseError => 1,
        PrintError => 0,
    });
}