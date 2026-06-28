---
skill_id: 67c358805f5f
usage_count: 1
last_used: 2026-06-16
---
# Good: Moo class
package User;
use Moo;
use Types::Standard qw(Str Int ArrayRef);
use namespace::autoclean;

has name  => (is => 'ro', isa => Str, required => 1);
has email => (is => 'ro', isa => Str, required => 1);
has age   => (is => 'ro', isa => Int, default  => sub { 0 });
has roles => (is => 'ro', isa => ArrayRef[Str], default => sub { [] });

sub is_admin($self) {
    return grep { $_ eq 'admin' } $self->roles->@*;
}

sub greet($self) {
    return "Hello, I'm " . $self->name;
}

1;