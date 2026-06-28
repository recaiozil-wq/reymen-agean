---
skill_id: 642a5e6d4829
usage_count: 1
last_used: 2026-06-16
---
# For strict production applications, manage schemas via Alembic migrations instead.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield