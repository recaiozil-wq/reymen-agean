---
skill_id: 89d9890fa278
usage_count: 1
last_used: 2026-06-16
---
# Resolve the storage target identifier from env based on provider
    if provider == "notion":
        db_id = os.environ.get("NOTION_DATABASE_ID")
        if not db_id:
            print("ERROR: NOTION_DATABASE_ID not set"); sys.exit(1)
    else: