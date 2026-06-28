---
skill_id: 87c973530934
usage_count: 1
last_used: 2026-06-16
---
# Disable migrations for speed
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()