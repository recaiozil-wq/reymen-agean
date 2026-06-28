---
skill_id: 8cf6753bfe36
usage_count: 1
last_used: 2026-06-16
---
# With an external pooler (PgBouncer, Supabase pooler)
DATABASE_URL="postgresql://user:pass@host/db?pgbouncer=true&connection_limit=1"
```

```ts
// Vercel, AWS Lambda, and similar serverless runtimes: cap pool to 1 per instance
// connection_limit and pool_timeout are controlled via DATABASE_URL
const prisma = new PrismaClient();
```