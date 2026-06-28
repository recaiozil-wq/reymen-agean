---
skill_id: d7cf1064f39e
usage_count: 1
last_used: 2026-06-16
---
# Good: Three-arg open with autodie (core module, eliminates 'or die')
use autodie;

sub read_file($path) {
    open my $fh, '<:encoding(UTF-8)', $path;
    local $/;
    my $content = <$fh>;
    close $fh;
    return $content;
}