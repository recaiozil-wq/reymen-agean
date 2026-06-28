---
skill_id: c4b57ebf6485
usage_count: 1
last_used: 2026-06-16
---
## Package Installation Patterns

### Basic Installation

```toml
[install]
nodejs.pkg-path = "nodejs"
python.pkg-path = "python311"
rustup.pkg-path = "rustup"
```

### Version Pinning

```toml
[install]
nodejs.pkg-path = "nodejs"
nodejs.version = "^20.0"          # Semver range: latest 20.x

postgres.pkg-path = "postgresql"
postgres.version = "16.2"         # Exact version
```

### Platform-Specific Packages

```toml
[install]