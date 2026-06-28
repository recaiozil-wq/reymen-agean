---
skill_id: 846f3878dc42
usage_count: 1
last_used: 2026-06-16
---
# Good: Validate column names against an allowlist
sub order_by($dbh, $column, $direction) {
    my %allowed_cols = map { $_ => 1 } qw(name email created_at);
    my %allowed_dirs = map { $_ => 1 } qw(ASC DESC);

    die "Invalid column: $column\n"    unless $allowed_cols{$column};
    die "Invalid direction: $direction\n" unless $allowed_dirs{uc $direction};

    my $sth = $dbh->prepare("SELECT * FROM users ORDER BY $column $direction");
    $sth->execute;
    return $sth->fetchall_arrayref({});
}