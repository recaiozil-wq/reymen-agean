---
skill_id: 21d65400601c
usage_count: 1
last_used: 2026-06-16
---
# IMPORTANT: gcc alone doesn't expose libstdc++ headers — you need gcc-unwrapped
gcc-unwrapped.pkg-path = "gcc-unwrapped"
gcc-unwrapped.pkg-group = "libraries"

cmake.pkg-path = "cmake"
cmake.pkg-group = "build"

gnumake.pkg-path = "gnumake"
gnumake.pkg-group = "build"

gdb.pkg-path = "gdb"
gdb.systems = ["x86_64-linux", "aarch64-linux"]
```