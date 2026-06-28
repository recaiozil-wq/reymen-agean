---
skill_id: 757c5fc0be7e
usage_count: 1
last_used: 2026-06-16
---
# Bad: Raw output in HTML
sub bad_html($input) {
    print "<div>$input</div>";  # XSS if $input contains <script>
}
```

### CSRF Protection

```perl
use v5.36;
use Crypt::URandom qw(urandom);
use MIME::Base64 qw(encode_base64url);

sub generate_csrf_token() {
    return encode_base64url(urandom(32));
}
```

Use constant-time comparison when verifying tokens. Most web frameworks (Mojolicious, Dancer2, Catalyst) provide built-in CSRF protection — prefer those over hand-rolled solutions.

### Session and Header Security

```perl
use v5.36;