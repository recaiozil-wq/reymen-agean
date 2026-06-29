---
name: ecc_prisma-patterns_references_with-an-external-pooler-pgbouncer-supabase-pooler
description: "With an external pooler (PgBouncer, Supabase pooler)"
title: "Ecc Prisma Patterns References With An External Pooler Pgbouncer Supabase Pooler"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | With an external pooler (PgBouncer, Supabase pooler) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# With an external pooler (PgBouncer, Supabase pooler)
DATABASE_URL="postgresql://user:pass@host/db?pgbouncer=true&connection_limit=1"
```

```ts
// Vercel, AWS Lambda, and similar serverless runtimes: cap pool to 1 per instance
// connection_limit and pool_timeout are controlled via DATABASE_URL
const prisma = new PrismaClient();
```
