---
skill_id: 6400709c4a32
usage_count: 1
last_used: 2026-06-16
---
# ...
}
```

### 3. Context Sensitivity

Understand scalar vs list context — a core Perl concept.

```perl
use v5.36;

my @items = (1, 2, 3, 4, 5);

my @copy  = @items;            # List context: all elements
my $count = @items;            # Scalar context: count (5)
say "Items: " . scalar @items; # Force scalar context
```

### 4. Postfix Dereferencing

Use postfix dereference syntax for readability with nested structures.

```perl
use v5.36;

my $data = {
    users => [
        { name => 'Alice', roles => ['admin', 'user'] },
        { name => 'Bob',   roles => ['user'] },
    ],
};