---
skill_id: 69f6f4d59ab3
usage_count: 1
last_used: 2026-06-16
---
# Log full details, return generic message
    logger.exception("Unexpected error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )
```