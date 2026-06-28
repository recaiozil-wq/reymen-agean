---
skill_id: 2a7ace8720cc
usage_count: 1
last_used: 2026-06-16
---
# GNU tools on macOS (where BSD defaults differ)
coreutils.pkg-path = "coreutils"
coreutils.systems = ["x86_64-darwin", "aarch64-darwin"]
```

### Resolving Package Conflicts

When two packages install the same binary, use `priority` (lower number wins):

```toml
[install]
gcc.pkg-path = "gcc12"
gcc.priority = 3

clang.pkg-path = "clang_18"
clang.priority = 5               # gcc wins file conflicts
```

Use `pkg-group` to group packages that should resolve versions together:

```toml
[install]
python.pkg-path = "python311"
python.pkg-group = "python-stack"

pip.pkg-path = "python311Packages.pip"
pip.pkg-group = "python-stack"    # Resolves together with python
```