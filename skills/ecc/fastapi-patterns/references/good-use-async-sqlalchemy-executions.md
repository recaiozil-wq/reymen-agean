---
skill_id: b1b265f5fab0
usage_count: 1
last_used: 2026-06-16
---
# Good: use async SQLAlchemy executions.
@router.get("/items/")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

---