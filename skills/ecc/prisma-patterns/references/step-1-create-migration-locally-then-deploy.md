---
skill_id: 6f3d61c24165
usage_count: 1
last_used: 2026-06-16
---
# Step 1: create migration locally, then deploy
npx prisma migrate dev --name add_new_column   # local only
npx prisma migrate deploy                       # staging / production
```

```ts
// Step 2: backfill data (run in a script or migration job, not in the shell)
await prisma.user.updateMany({ data: { newColumn: derivedValue } });
```

```bash