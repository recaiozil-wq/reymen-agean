---
skill_id: 5538c5c3f13c
usage_count: 1
last_used: 2026-06-16
---
# Generate client after schema changes
npx prisma generate
```

### Schema Example

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  avatarUrl String?  @map("avatar_url")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  orders    Order[]

  @@map("users")
  @@index([email])
}
```

### Custom SQL Migration

For operations Prisma cannot express (concurrent indexes, data backfills):

```bash