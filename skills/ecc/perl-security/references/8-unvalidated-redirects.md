---
skill_id: a6e332a69990
usage_count: 1
last_used: 2026-06-16
---
# 8. Unvalidated redirects
print $cgi->redirect($user_url);         # Open redirect
```

**Remember**: Perl's flexibility is powerful but requires discipline. Use taint mode for web-facing code, validate all input with allowlists, use DBI placeholders for every query, and encode all output for its context. Defense in depth — never rely on a single layer.