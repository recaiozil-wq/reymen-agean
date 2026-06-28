---
skill_id: 8f382f60d5b1
usage_count: 1
last_used: 2026-06-16
---
# Prisma Patterns

Production patterns and non-obvious traps for Prisma ORM in TypeScript backends.
Tested against Prisma 5.x and 6.x. Some behaviors differ from Prisma 4.

Check the Prisma version before applying version-specific patterns:

```bash
npx prisma --version
```

Prisma 5 introduced `relationJoins`, which can load relations via JOIN rather than separate queries depending on query strategy and configuration. The `omit` field modifier and `prisma.$extends` Client Extensions API were also added. Note: `relationJoins` can cause row explosion on large 1:N relations or deep nested `include` — benchmark both approaches when relations may return many rows per parent.