---
skill_id: 03c21e45a588
usage_count: 1
last_used: 2026-06-16
---
# Bad: sync DB calls in async routes block the event loop.
@router.get("/items/")
async def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()