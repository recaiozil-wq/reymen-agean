---
skill_id: a0f848942ce8
usage_count: 1
last_used: 2026-06-16
---
# Setup
    my $dir = tempdir(CLEANUP => 1);
    my $file = path($dir, 'input.txt');
    $file->spew_utf8("line1\nline2\nline3\n");