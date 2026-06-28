---
skill_id: 0892f30d7543
usage_count: 1
last_used: 2026-06-16
---
# Prefer project-locked versions. If using a tag, use a pinned version per project policy.
set(GTEST_VERSION v1.17.0) # Adjust to project policy.
FetchContent_Declare(
  googletest