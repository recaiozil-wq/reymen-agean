---
skill_id: 2e5b36e5339e
usage_count: 1
last_used: 2026-06-16
---
# Good: Three-arg open, lexical filehandle, check return
sub read_file($path) {
    open my $fh, '<:encoding(UTF-8)', $path
        or die "Cannot open '$path': $!\n";
    local $/;
    my $content = <$fh>;
    close $fh;
    return $content;
}