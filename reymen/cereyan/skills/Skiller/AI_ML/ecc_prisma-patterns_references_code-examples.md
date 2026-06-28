---
name: ecc_prisma-patterns_references_code-examples
description: Code Examples
title: "Ecc Prisma Patterns References Code Examples"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Code Examples |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Code Examples

### Cursor Pagination (preferred for feeds and large datasets)

```ts
async function getPosts(cursor?: string, limit = 20) {
  const items = await prisma.post.findMany({
    where: { published: true },
    orderBy: [
      { createdAt: 'desc' },
      { id: 'desc' }, // secondary sort prevents unstable pagination on duplicate timestamps
    ],
    take: limit + 1,
    ...(cursor && { cursor: { id: cursor }, skip: 1 }),
  });

  const hasNextPage = items.length > limit;
  if (hasNextPage) items.pop();

  return { items, nextCursor: hasNextPage ? items[items.length - 1].id : null };
}
```

Fetch `limit + 1` and pop — canonical way to detect `hasNextPage` without an extra count query. Always include a unique field (e.g. `id`) as a secondary `orderBy` to prevent unstable pagination when multiple rows share the same timestamp. Use offset pagination only when users need to jump to arbitrary pages (admin tables).

### Soft Delete

```ts
// Always filter explicitly — do not rely on middleware (hides behavior, hard to debug)
const activeUsers = await prisma.user.findMany({ where: { deletedAt: null } });

await prisma.user.update({ where: { id }, data: { deletedAt: new Date() } });
await prisma.user.update({ where: { id }, data: { deletedAt: null } }); // restore
```

### Error Handling

```ts
import { Prisma } from '@prisma/client';

try {
  await prisma.user.create({ data: { email } });
} catch (e) {
  if (e instanceof Prisma.PrismaClientKnownRequestError) {
    if (e.code === 'P2002') throw new ConflictError('Email already exists');
    if (e.code === 'P2025') throw new NotFoundError('Record not found');
    if (e.code === 'P2003') throw new BadRequestError('Referenced record does not exist');
  }
  throw e;
}
```

Common codes: `P2002` unique violation · `P2025` not found · `P2003` foreign key violation.

Catch at the service boundary and translate to domain errors. Never expose raw Prisma messages to API consumers.

### Connection Pool — Serverless

Embed connection params directly in `DATABASE_URL` — string concatenation breaks if the URL already has query parameters (e.g. `?schema=public`):

```bash
