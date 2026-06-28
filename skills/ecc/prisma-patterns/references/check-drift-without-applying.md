---
skill_id: 7e17ad48f8af
usage_count: 1
last_used: 2026-06-16
---
# Check drift without applying
npx prisma migrate diff \
  --from-migrations ./prisma/migrations \
  --to-schema-datamodel ./prisma/schema.prisma \
  --shadow-database-url "$SHADOW_DATABASE_URL"
```

### Manually editing a migration file breaks future deploys

Prisma checksums every migration file. Editing after apply causes `P3006 checksum mismatch` on every environment where the original already ran. Create a new migration instead.

### Breaking schema changes require multi-step migration

Adding `NOT NULL` to an existing column or renaming a column in one migration will lock the table or drop data. Use expand-and-contract:

```bash